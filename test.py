# load blocking bounds
import schedcat.model.tasks as tasks

import schedcat.model.resources as resources

import schedcat.locking.bounds as bounds

import schedcat.sched.edf as edf

from example.mapping import partition_tasks

import itertools

# initialize the resource model
ts = tasks.TaskSystem([tasks.SporadicTask(2,3),
                           tasks.SporadicTask(1,3),
                           tasks.SporadicTask(2,3)])

resources.initialize_resource_model(ts)

ts[0].resmodel[0].add_request(1)
ts[1].resmodel[0].add_request(1)

clusts = partition_tasks(1, 2, False, ts)


omlp_ts = ts.copy()

omlp_clusts = partition_tasks(1,2,False,omlp_ts)

edf.bound_response_times(2, ts)
edf.bound_response_times(2, omlp_ts)



bounds.assign_edf_preemption_levels(ts)
# inflate execution costs by blocking terms
bounds.apply_part_fmlp_bounds(ts)

bounds.assign_edf_preemption_levels(omlp_ts)
bounds.apply_clustered_omlp_bounds(omlp_ts,1)

print ts[0].cost,omlp_ts[0].cost, ts[1].cost,omlp_ts[1].cost, ts[2].cost,omlp_ts[2].cost

for clust in omlp_clusts:
    for task in clust:
        print task.cost


# test schedulability
#edf.is_schedulable(3, ts)
True
print "all done?"