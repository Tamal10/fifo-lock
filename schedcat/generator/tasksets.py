"""
Generate random task sets for schedulability experiments.
"""


import re
import random
from functools import partial

import schedcat.generator.tasks as gen

def decode_params(name):
    # uni-UMIN-UMAX-PMIN-PMAX    
    # bimo-
    # exp-UMIN-UMAX-MEAN-PMIN-PMAX
    
    pass

NAMED_PERIODS = {
# Named period distributions used in several UNC papers, in milliseconds.
    'unishort'     : gen.uniform_int( 3,  33),
    'unimoderate'  : gen.uniform_int(10, 100),
    'unilong'      : gen.uniform_int(50, 250),

    #'logunishort'     : gen.log_uniform_int( 3,  33),
    #'logunimoderate'  : gen.log_uniform_int(10, 100),
    #'logunilong'      : gen.log_uniform_int(50, 250),
    }

NAMED_UTILIZATIONS = {
# Named utilization distributions used in several UNC papers, in milliseconds.
    'unilight'     : gen.uniform(0.001, 0.1),
    'unimedium'    : gen.uniform(0.1  , 0.4),
    'uniheavy'     : gen.uniform(0.5  , 0.9),

    #'explight'     : gen.exponential(0, 1, 0.10),
    #'expmedium'    : gen.exponential(0, 1, 0.25),
    #'expheavy'     : gen.exponential(0, 1, 0.50),

    #'bimolight'    : gen.multimodal([(gen.uniform(0.001, 0.5), 8),
    #                               (gen.uniform(0.5  , 0.9), 1)]),
    #'bimomedium'   : gen.multimodal([(gen.uniform(0.001, 0.5), 6),
    #                                  (gen.uniform(0.5  , 0.9), 3)]),
    #'bimoheavy'    : gen.multimodal([(gen.uniform(0.001, 0.5), 4),
    #                                  (gen.uniform(0.5  , 0.9), 5)]),
}

def uniform_slack(min_slack_ratio, max_slack_ratio):
    """Choose deadlines uniformly such that the slack
       is within [cost + min_slack_ratio * (period - cost),
                  cost + max_slack_ratio * (period - cost)].
                  
        Setting max_slack_ratio = 1 implies constrained deadlines.
    """
    def choose_deadline(cost, period):
        slack = period - cost
        earliest = slack * min_slack_ratio
        latest   = slack * max_slack_ratio
        return cost + random.uniform(earliest, latest)
    return choose_deadline

NAMED_DEADLINES = {
    'implicit'        : None,
    'uni-constrained' : uniform_slack(0, 1),
    'uni-arbitrary'   : uniform_slack(0, 2),
}

def mkgen(utils, periods, deadlines=None):
    if deadlines is None:
        g = gen.TaskGenerator(periods, utils)
    else:
        g = gen.TaskGenerator(periods, utils, deadlines)
    return partial(g.make_task_set)

def make_standard_dists(dl='implicit'):
    by_period = {}
    for p in NAMED_PERIODS:
        by_util = {}
        by_period[p] = by_util
        for u in NAMED_UTILIZATIONS:
                by_util[u] = mkgen(NAMED_UTILIZATIONS[u],
                                   NAMED_PERIODS[p],
                                   NAMED_DEADLINES[dl])
    return by_period

# keyed by deadline type, then by period, then by utilization
DIST_BY_KEY = {}
for dl in NAMED_DEADLINES:
    DIST_BY_KEY[dl] = make_standard_dists(dl)

ALL_DISTS = {}
for dl in NAMED_DEADLINES:
    for p in NAMED_PERIODS:
        for u in NAMED_UTILIZATIONS:
            ALL_DISTS[':'.join([u, p, dl])] = DIST_BY_KEY[dl][p][u]
