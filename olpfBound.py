


def compute_olpf_bound(ts, num_proc, nres):

    per_resource_L_sum = [0 for i in range(nres)]
    #num_issuer = [0 for i in range(nres)]
    all_cost_list = []

    for res_id in range(nres):
        cost_list = []
        for task in ts:
            cost_list.append(task.resmodel[res_id].max_write_length)

        cost_list = sorted(cost_list,reverse=True)
        all_cost_list.append(cost_list)
        #print cost_list, num_proc
        for i in range(min(len(cost_list)-1, num_proc-1)):
            per_resource_L_sum[res_id] += cost_list[i]

    for task in ts:
        blocking  = 0
        for res_id in range(nres):
            cost_list = all_cost_list[res_id]
            L_sum = 0
            j = 0
            for i in range(min(len(cost_list) - 1, num_proc - 1)):
                if i == j and cost_list[i] == task.resmodel[res_id].max_write_length:
                    j += 1
                L_sum += cost_list[j]
                j += 1
            blocking += (L_sum * task.resmodel[res_id].max_writes)
            #print res_id, blocking
        #print task.cost, blocking
        task.cost += blocking

def compute_olpf_bound_for_rw(ts, num_proc, nres):

    per_resource_L_sum = [0 for i in range(nres)]
    #num_issuer = [0 for i in range(nres)]
    all_cost_list = []

    for res_id in range(nres):
        cost_list = []
        for task in ts:
            cost_list.append(max(task.resmodel[res_id].max_write_length,task.resmodel[res_id].max_read_length))

        cost_list = sorted(cost_list,reverse=True)
        all_cost_list.append(cost_list)
        #print cost_list, num_proc
        for i in range(min(len(cost_list)-1, num_proc-1)):
            per_resource_L_sum[res_id] += cost_list[i]

    for task in ts:
        blocking  = 0
        for res_id in range(nres):
            cost_list = all_cost_list[res_id]
            L_sum = 0
            j = 0
            for i in range(min(len(cost_list) - 1, num_proc - 1)):
                if i == j and cost_list[i] == task.resmodel[res_id].max_write_length:
                    j += 1
                L_sum += cost_list[j]
                j += 1
            blocking += (L_sum * task.resmodel[res_id].max_writes)
            #print res_id, blocking
        #print task.cost, blocking
        task.cost += blocking


def compute_rw_olpf_bound(ts, num_proc, nres):
    per_resource_L_max = [0 for i in range(nres)]
    per_resource_L_read = [0 for i in range(nres)]
    per_resource_L_write = [0 for i in range(nres)]
    per_resource_L_max_read = [0 for i in range(nres)]
    per_resource_L_max_write = [0 for i in range(nres)]
    all_write_costs = []
    all_read_costs = []

    for res_id in range(nres):
        cost_list = []
        read_cost_list = []
        for task in ts:
            per_resource_L_max[res_id] = max(per_resource_L_max[res_id], task.resmodel[res_id].max_write_length,task.resmodel[res_id].max_read_length)
            per_resource_L_max_read[res_id] = max(per_resource_L_max_read[res_id], task.resmodel[res_id].max_read_length)
            per_resource_L_max_write[res_id] = max(per_resource_L_max_write[res_id], task.resmodel[res_id].max_write_length)
            cost_list.append(task.resmodel[res_id].max_write_length)
            read_cost_list.append(task.resmodel[res_id].max_read_length)

        sorted(cost_list,reverse=True)
        sorted(read_cost_list,reverse=True)
        all_write_costs.append(cost_list)
        all_read_costs.append(read_cost_list)

        per_resource_L_read[res_id] =  (per_resource_L_max_read[res_id] + per_resource_L_max_write[res_id]-1)
        per_resource_L_write[res_id] = (2*num_proc-3) * per_resource_L_max[res_id]



    for task in ts:
        blocking = 0

        for res_id in range(nres):
            read_cost_list = all_read_costs[res_id]
            write_cost_list = all_write_costs[res_id]

            read_blocking = 0
            write_blocking = 0
            write_blocking_by_read_request = 0

            # blocking for read requests
            for i in range(min(1, len(read_cost_list)-1)):
                if task.resmodel[res_id].max_read_length == read_cost_list[i]:
                    read_blocking += (read_cost_list[i+1]-1)
                else:
                    read_blocking += (read_cost_list[i]-1)
                write_blocking_by_read_request = read_blocking + 1
            for i in range(min(1, len(write_cost_list)-1)):
                if task.resmodel[res_id].max_write_length == write_cost_list[i]:
                    read_blocking += (write_cost_list[i+1])
                else:
                    read_blocking += (write_cost_list[i])

            #blocking for write requests
            #case 1: m-1 write length + (m-2) read length (read lengths all should be max_read_len other than the job's reads)
            # case 2: m-2 read length + (m-1) write length
            write_blocking_case1 = 0
            write_blocking_case2 = 0
            j=0
            for i in range(min(num_proc-1, len(write_cost_list)-1)):
                if i == j and write_cost_list[i] == task.resmodel[res_id].max_write_length:
                    j += 1
                write_blocking_case1 += write_cost_list[j]
                if i != num_proc-1:
                    write_blocking_case2 += write_cost_list[j]
                j += 1

            read_blocking_case1 = min(num_proc-2, len(write_cost_list)-1) * write_blocking_by_read_request
            read_blocking_case2 = min(num_proc-1, len(write_cost_list)-1) * write_blocking_by_read_request
            write_blocking = max(write_blocking_case1 + read_blocking_case1, write_blocking_case2 + read_blocking_case2)

            blocking += (read_blocking * task.resmodel[res_id].max_reads + write_blocking * task.resmodel[res_id].max_writes)
        task.cost += blocking

def compute_omlp_bound(ts, num_proc, nres):
    per_resource_L_sum = [0 for i in range(nres)]
    for res_id in range(nres):
        cost_list = []
        for task in ts:
            per_resource_L_sum[res_id] = max(per_resource_L_sum[res_id], task.resmodel[res_id].max_write_length)
        per_resource_L_sum[res_id] = (2*num_proc - 1 )*per_resource_L_sum[res_id]

    for task in ts:
        blocking  = 0
        for res_id in range(nres):
            blocking += (per_resource_L_sum[res_id] * task.resmodel[res_id].max_writes)
        task.cost += blocking


