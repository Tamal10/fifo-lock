import schedcat.model.tasks as tasks

import schedcat.model.resources as resources

import schedcat.locking.bounds as bounds

import schedcat.sched.edf as edf

import schedcat.sched.edf.da as da

from example.mapping import partition_tasks

import itertools

from olpfBound import compute_olpf_bound

# initialize the resource model
ts = tasks.TaskSystem([tasks.SporadicTask(2,3),
                           tasks.SporadicTask(1,3),
                           tasks.SporadicTask(2,3), tasks.SporadicTask(1,6), tasks.SporadicTask(3,9), tasks.SporadicTask(5,11)]
                      )

resources.initialize_resource_model(ts)

ts[0].resmodel[0].add_request(1)
ts[0].resmodel[1].add_request(1)
ts[1].resmodel[0].add_request(1)
ts[2].resmodel[0].add_request(1)
ts[3].resmodel[0].add_request(1)
ts[4].resmodel[0].add_request(1)
ts[4].resmodel[0].add_request(1)
ts[4].resmodel[0].add_request(1)

omlp_ts = ts.copy()



olpf_ts = ts.copy()

comlp_ts = ts.copy()

compute_olpf_bound(olpf_ts, 10, 2)

da.bound_response_times(10,omlp_ts)
print omlp_ts[4].resmodel[0].max_writes, omlp_ts[4].response_time

for t in omlp_ts: t.partition = 0

bounds.assign_edf_preemption_levels(omlp_ts)

bounds.apply_global_omlp_bounds(omlp_ts, 10)

da.bound_response_times(10,comlp_ts)

for t in comlp_ts: t.partition = 0

bounds.assign_edf_preemption_levels(comlp_ts)

bounds.apply_clustered_omlp_bounds(comlp_ts, 10, 10)

print olpf_ts, omlp_ts, comlp_ts
