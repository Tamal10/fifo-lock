import argparse
from Constants import Constants
from TaskSetGenaration import TaskGen

import schedcat.sched.edf as edf
#import schedcat.sched.edf.da as da

import schedcat.locking.bounds as bounds

from olpfBound import compute_olpf_bound, compute_olpf_bound_for_rw, compute_rw_olpf_bound

import itertools
from csv import DictWriter


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
                      str(int(float(scenario['pacc'])*10)),
                      str(int(float(scenario['sys_util']) * 10)),
                      str(int(float(scenario['pwrite'])*10)),
                      str(int(scenario['nres']),
                          )
                      ])


def single_exp(period, util, sys_util, nres, pacc, cslen, proc, task_generator, pwrite):
    ts = task_generator.create_rw_task(pwrite)

    if not edf.da.bound_response_times(proc, ts):
        return

    olpf_ts = ts.copy()
    omlp_ts = ts.copy()
    comlp_ts = ts.copy()
    omlp_test_ts = ts.copy()
    omip_ts = ts.copy()
    fmlp_sob_ts = ts.copy()

    olpf_schedulable = 0
    omlp_schedulable = 0
    comlp_schedulable = 0
    omip_schedulable = 0
    fmlp_sob_schedulable = 0


    for t in comlp_ts: t.partition = 0

    bounds.assign_edf_preemption_levels(comlp_ts)
    bounds.apply_clustered_rw_omlp_bounds(comlp_ts, proc)
    if edf.da.bound_response_times(proc, comlp_ts):
        comlp_schedulable = 1

    #omip = rw-olpf
    for t in omip_ts: t.partition = 0

    # bounds.assign_edf_preemption_levels(olpf_ts)
    compute_rw_olpf_bound(omip_ts, proc, nres)

    if edf.da.bound_response_times(proc, omip_ts):
        omip_schedulable = 1

    for t in olpf_ts: t.partition = 0

    # bounds.assign_edf_preemption_levels(olpf_ts)
    compute_olpf_bound_for_rw(olpf_ts, proc, nres)

    if edf.da.bound_response_times(proc, olpf_ts):
        olpf_schedulable = 1

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
    pwrite = scenario['pwrite']

    sys_util = scenario['sys_util'] * proc

    task_generator = TaskGen(period, util, sys_util, nres, pacc, cslen)

    while numSamples < Constants.MAX_SAMPLES:
        omlp_schedulable, comlp_schedulable, omip_schedulable, fmlp_sob_schedulable, olpf_schedulable = \
            single_exp(period, util, sys_util, nres, pacc, cslen, proc, task_generator, pwrite)
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


def generateScenario(numCores, accessProbability, period, csLen, numRes, utilDist, normalizedUtil, pwrite):
    # goal: return a scenario corresponding to every possible combination

    paramList = {}

    paramList['proc'] = [numCores]

    paramList['pacc'] = [accessProbability]

    paramList['period'] = [period]

    paramList['cslen'] = [csLen]

    paramList['nres'] = [numRes]

    paramList['util'] = [utilDist]

    paramList['sys_util'] = [normalizedUtil]

    paramList['pwrite'] = [pwrite]

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
    parser.add_argument('-w', "--pwrite", default="All", help="Write probability")

    args = parser.parse_args()
    numCores = int(args.processors)
    accessProbability = float(args.pacc)
    period = args.period
    csLen = args.cslen
    numRes = int(args.numres)
    utilDist = args.util
    normalizedUtil = float(args.sysutil)
    pwrite = float(args.pwrite)

    scenarios = generateScenario(numCores, accessProbability, period, csLen, numRes, utilDist, normalizedUtil, pwrite)

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
        outfiles_abs[title(scenario)] = DictWriter(open('results_rw/' + title(scenario) + ".csv", 'w'),
                                                   fieldnames=fieldnames)

        outfiles_abs[title(scenario)].writeheader()

        dp.append((scenario))
    seq_dps(dp, outfiles_abs)
    return


if __name__ == '__main__':
    main()