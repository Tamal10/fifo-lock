import math

import schedcat.model.tasks as tasks



def RBF(task_i,A):
    alpha_i = math.ceil(A*1.0/task_i.period)
    #print "alpha_i", alpha_i, A*1.0/task_i.period, A, task_i.period
    return int(alpha_i) * int(task_i.cost)

def compute_RBF_sum(ts,A):
    return sum(RBF(task_i,A) for task_i in ts)

def compute_L(ts):
    L = 1
    while True:
        x = compute_RBF_sum(ts,L)
        #print x, L
        if x==L:
            #print L
            return L
        L = x

def compute_R(ts):
    L = compute_L(ts)
    R = 0
    for i in range(1,L):
        R = max(R, compute_RBF_sum(ts,i+1) - i)
    return R

def fifo_sched_test(ts):
    U_sum = sum(task.cost*1.0/task.period for task in ts)
    #print U_sum
    if U_sum > 1:
        return None
    R = compute_R(ts)
    #print R
    for task in ts:
        if R > task.deadline:
            return False
    return True


def edf_sched_test(ts):
    #deadline >= period
    U_sum = sum(task.cost * 1.0 / task.period for task in ts)
    # print U_sum
    if U_sum > 1:
        return False
    return True

if __name__ == '__main__':
    ts = tasks.TaskSystem([tasks.SporadicTask(1, 4, 50),
                           tasks.SporadicTask(30, 50, 50)])

    print fifo_sched_test(ts)