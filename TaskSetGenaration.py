from schedcat.model.tasks import SporadicTask, TaskSystem
from schedcat.generator.tasks import exponential, uniform, multimodal
from schedcat.generator.tasksets import  NAMED_UTILIZATIONS
from schedcat.generator.generator_emstada import gen_taskset, NAMED_PERIODS
from schedcat.util.storage import storage
import schedcat.sched.edf as edf
import schedcat.model.resources as resources
import schedcat.generator.tasks as tasks

from schedcat.util.time import ms2us

import random

CSLENGTH = { 'short'  : lambda: random.randint(1,   15),
             'medium' : lambda: random.randint(1,  100),
             'long'   : lambda: random.randint(5, 1280), }

class TaskGen:
    def __init__(self, period, util, sys_util,  nres, pacc, cslen):
        self.period = period
        self.task_util = util
        self.sys_util = sys_util
        self.nres = nres
        self.pacc = pacc
        self.cslen = cslen
    def create_task(self):

        '''tg = tasks.TaskGenerator(period = NAMED_PERIODS[self.period],
                                        util   = NAMED_UTILIZATIONS[self.task_util])

        ts = tg.make_task_set(max_util = self.sys_util, squeeze = True, time_conversion=ms2us)'''

        tasks_n = random.randint(int(self.sys_util*2), 150)

        ts = gen_taskset(self.period, "unif", tasks_n, self.sys_util)

        resources.initialize_resource_model(ts)

        for task in ts:
            sum = task.cost
            for res_id in range(self.nres):
                if random.random() < self.pacc:
                    nreqs = random.randint(1, 5)
                    length = CSLENGTH[self.cslen]
                    #rem = sum - nreqs * length
                    #if rem < 0:
                    #    length = sum // nreqs
                    #sum -= nreqs*length
                    for j in range(nreqs):
                        len = length()
                        rem = sum - len
                        if rem < 0:
                            len = sum - rem
                        sum -= len
                        task.resmodel[res_id].add_request(len)
                        if sum == 0:
                            nreqs = j+1
                if sum == 0:
                    break

        #bounds.assign_edf_preemption_levels(ts)
            #print task

        return ts

    def create_rw_task(self, pwrite):
        '''tg = tasks.TaskGenerator(period=NAMED_PERIODS[self.period],
                                 util=NAMED_UTILIZATIONS[self.task_util])

        ts = tg.make_task_set(max_util=self.sys_util, squeeze=True, time_conversion=ms2us)'''

        tasks_n = random.randint(int(self.sys_util * 2), 150)

        ts = gen_taskset(self.period, "unif", tasks_n, self.sys_util)

        resources.initialize_resource_model(ts)

        for task in ts:
            sum = task.cost
            for res_id in range(self.nres):
                if random.random() < self.pacc:
                    nreqs = random.randint(1, 5)
                    length = CSLENGTH[self.cslen]
                    # rem = sum - nreqs * length
                    # if rem < 0:
                    #    length = sum // nreqs
                    # sum -= nreqs*length
                    for j in range(nreqs):
                        len = length()
                        rem = sum - len
                        if rem < 0:
                            len = sum - rem
                        sum -= len
                        if random.random() < pwrite:
                            task.resmodel[res_id].add_write_request(len)
                        else:
                            task.resmodel[res_id].add_read_request(len)
                        if sum == 0:
                            nreqs = j + 1
                if sum == 0:
                    break

        # bounds.assign_edf_preemption_levels(ts)
        # print task

        return ts


if __name__ == '__main__':
    task_generator = TaskGen('unilong','unilight', 8, 16, 0.1, 'long')
    ts = task_generator.create_task()

    for task in ts:
        print task.cost, task.period
        count = 0
        for i in range(16):
            count += task.resmodel[i].max_writes
        print(count)
        print "----"