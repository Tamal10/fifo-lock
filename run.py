import argparse
from Constants import  Constants
from TaskSetGenaration import TaskGen

import schedcat.sched.edf as edf

import schedcat.sched.edf.da as da

import schedcat.locking.bounds as bounds

from olpfBound import compute_olpf_bound, compute_omlp_bound

import itertools
from csv import DictWriter

from exp_rw import seq_dps, generateScenario, title

from schedcat.generator.tasksets import NAMED_PERIODS, NAMED_UTILIZATIONS
from TaskSetGenaration import  CSLENGTH


taskUtilList = NAMED_UTILIZATIONS.keys()
periodDist = NAMED_PERIODS.keys()
csLen = CSLENGTH.keys()
coreCounts = [4,8]
#for core in Constants.NUM_PROC:
#    coreCounts.append(str(core))
#maxPeriodList = Constants.PERIOD_MAX
count = 1

# make sure critUtilList is ordered by priority
for m in coreCounts:

    for p in Constants.PACC:
        for task_util in ['unilight']:
            for period in periodDist:
                num_res = [m//4, m//2, m, 2*m]
                for nres in num_res:
                    for cs in csLen:
                        for pwrite in Constants.PWRITE:
                            for u in [0.2,0.3]: #  Constants.NORM_UTILS:
                                '''if count < 649:
                                    count += 1
                                    continue'''

                                print count
                                count += 1

                                scenarios = generateScenario(m, p, period, cs, nres, task_util, u, pwrite)

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
                                    outfiles_abs[title(scenario)] = DictWriter(
                                        open('results_rw/' + title(scenario) + ".csv", 'w'),
                                        fieldnames=fieldnames)

                                    outfiles_abs[title(scenario)].writeheader()

                                    dp.append((scenario))
                                seq_dps(dp, outfiles_abs)