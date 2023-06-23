import argparse
from Constants import Constants
from TaskSetGenaration import TaskGen

import schedcat.sched.edf as edf

import schedcat.sched.edf.da as da

import schedcat.locking.bounds as bounds

from olpfBound import compute_olpf_bound, compute_omlp_bound

import itertools
from csv import DictWriter
from example.mapping import partition_tasks

from uniSchedTest import fifo_sched_test

import random


def title(scenario):
    '''norm_util = scenario['sys_util']/scenario['proc']
    for n_u in Constants.NORM_UTILS:
        if norm_util >= n_u - 0.0001 and norm_util <= n_u + 0.0001:
            norm_util = n_u
            break'''

    return '__'.join([str(scenario['proc']),
                      str(scenario['util']),
                      str(scenario['period']),
                      str(scenario['cslen']),
                      str(int(float(scenario['pacc']) * 10)),
                      str(int(float(scenario['sys_util']) * 10)),
                      str(int(scenario['nres']),
                          )
                      ])


def single_exp(period, util, sys_util, nres, pacc, cslen, proc, task_generator):
    ts = task_generator.create_task()

    for task in ts:
        task.deadline =  random.randint(task.period, 2*task.period)

    if not da.bound_response_times(proc,ts):
        return
    clusts = partition_tasks(1, proc, False, ts)

    olpf_ts = ts.copy()
    omlp_ts = ts.copy()
    comlp_ts = ts.copy()
    omip_ts = ts.copy()
    fmlp_sob_ts = ts.copy()

    olpf_clusts = partition_tasks(1, proc, False, olpf_ts)
    omlp_clusts = partition_tasks(1, proc, False, omlp_ts)
    comlp_clusts = partition_tasks(1, proc, False, comlp_ts)

    if olpf_clusts == False:
        return 0,0,0,0,0

    olpf_schedulable = 1
    omlp_schedulable = 0
    comlp_schedulable = 1
    omip_schedulable = 0
    fmlp_sob_schedulable = 0


    bounds.assign_edf_preemption_levels(comlp_ts)
    bounds.apply_clustered_omlp_bounds(comlp_ts, proc)

    for clust in comlp_clusts:
        if not edf.bound_response_times(1, clust):
            comlp_schedulable = 0



    # bounds.assign_edf_preemption_levels(olpf_ts)
    compute_olpf_bound(olpf_ts, proc, nres)

    for clust in olpf_clusts:
        if not fifo_sched_test(clust):
            olpf_schedulable = 0


    return omlp_schedulable, comlp_schedulable, omip_schedulable, fmlp_sob_schedulable, olpf_schedulable


def schedStudySingleScenarioUtil(scenario):
    numSamples = 0
    num_schedulable = {Constants.GOMLP: 0, Constants.COMLP: 0, Constants.OMIP: 0,
                       Constants.FMLP: 0, Constants.OLPF: 0}

    period = scenario['period']
    util = scenario['util']

    nres = scenario['nres']
    pacc = scenario['pacc']
    cslen = scenario['cslen']
    proc = scenario['proc']

    sys_util = scenario['sys_util'] * proc

    task_generator = TaskGen(period, util, sys_util, nres, pacc, cslen)

    while numSamples < Constants.MAX_SAMPLES:
        omlp_schedulable, comlp_schedulable, omip_schedulable, fmlp_sob_schedulable, olpf_schedulable = \
            single_exp(period, util, sys_util, nres, pacc, cslen, proc, task_generator)
        #print omlp_schedulable, comlp_schedulable, omip_schedulable, fmlp_sob_schedulable, olpf_schedulable
        num_schedulable[Constants.COMLP] += comlp_schedulable
        num_schedulable[Constants.GOMLP] += omlp_schedulable
        num_schedulable[Constants.OMIP] += omip_schedulable
        num_schedulable[Constants.FMLP] += fmlp_sob_schedulable
        num_schedulable[Constants.OLPF] += olpf_schedulable
        numSamples += 1

    acceptance_ratio = {k: num_schedulable.get(k, 0) * 1.0 / numSamples for k in
                        set(num_schedulable)}

    return scenario, acceptance_ratio


def schedStudySingleScenarioUtilUnpack(in_data):
    scenario = in_data
    return schedStudySingleScenarioUtil(scenario)


def seq_dps(dp, outfiles_abs):
    total_dp = len(dp)
    completed_dp = 0
    completed_dp_percent = 0
    for designpoint in dp:
        scenario, acceptance_ratio = schedStudySingleScenarioUtilUnpack(designpoint)
        rowDict = {
            'm': scenario['proc'],
            'OMLP': acceptance_ratio[Constants.GOMLP],
            'COMLP': acceptance_ratio[Constants.COMLP],
            'OMIP': acceptance_ratio[Constants.OMIP],
            'FMLP': acceptance_ratio[Constants.FMLP],
            'OLPF': acceptance_ratio[Constants.OLPF]
        }

        outfiles_abs[title(scenario)].writerow(rowDict)

        completed_dp += 1
        if int(100 * completed_dp / total_dp) > completed_dp_percent:
            completed_dp_percent = int(100 * completed_dp / total_dp)
            print('Completed %d%%' % completed_dp_percent)


def generateScenario(numCores, accessProbability, period, csLen, numRes, utilDist, normalizedUtil):
    # goal: return a scenario corresponding to every possible combination

    paramList = {}

    paramList['proc'] = [numCores]

    paramList['pacc'] = [accessProbability]

    paramList['period'] = [period]

    paramList['cslen'] = [csLen]

    paramList['nres'] = [numRes]

    paramList['util'] = [utilDist]

    paramList['sys_util'] = [normalizedUtil]

    keys = paramList.keys()

    vals = paramList.values()
    for instance in itertools.product(*vals):
        yield dict(zip(keys, instance))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', "--processors", default="All", type=int, help="Number of cores")
    parser.add_argument('-c', "--cslen", default="All", help="CS length")
    parser.add_argument('-t', "--period", default="All", help="Task period distribution")
    parser.add_argument('-u', "--util", default="All", help="Util distribution")
    parser.add_argument('-p', "--pacc", default="All", help="Access probability")
    parser.add_argument('-r', "--numres", default="All", help="Number of resource")
    parser.add_argument('-s', "--sysutil", default="All", help="Normalized utilization")

    args = parser.parse_args()
    numCores = int(args.processors)
    accessProbability = float(args.pacc)
    period = args.period
    csLen = args.cslen
    numRes = int(args.numres)
    utilDist = args.util
    normalizedUtil = float(args.sysutil)

    scenarios = generateScenario(numCores, accessProbability, period, csLen, numRes, utilDist, normalizedUtil)

    dp = []
    # output
    outfiles_abs = {}
    # outfiles_rel = {}

    fieldnames = ['m',
                  'OMLP',
                  'COMLP',
                  'OMIP',
                  'FMLP',
                  'OLPF'
                  ]
    # fieldnames.extend(['AVG_NUM_TASKS'])

    for scenario in scenarios:
        outfiles_abs[title(scenario)] = DictWriter(open('results_part/' + title(scenario) + ".csv", 'w'),
                                                   fieldnames=fieldnames)

        outfiles_abs[title(scenario)].writeheader()

        dp.append((scenario))
    seq_dps(dp, outfiles_abs)
    return


if __name__ == '__main__':
    main()