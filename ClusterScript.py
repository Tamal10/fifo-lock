from Constants import Constants
from schedcat.generator.tasksets import NAMED_PERIODS, NAMED_UTILIZATIONS
from TaskSetGenaration import  CSLENGTH
import sys

'''if len(sys.argv) < 2:
    print("Usage:", sys.argv[0], "<email> <period configuration> <core count>")
    print(" <email> is your @university.edu email address (not cs)")
    #print(" <period configuration> is one of", list(Constants.PERIOD_MAX))
    exit(1)'''

#email = sys.argv[1]
#period = sys.argv[2]


# sbatch -p general -N 1 --mem 32g -n 1 -c 24 -t 0:20:00 --mail-type=end --mail-user=stamal@live.unc.edu --wrap="python3 sched_study.py --period Short --smt High"

# this is the variable part
baseCommand = "sbatch -p general -N 1 --mem 128g -n 1 -c 24 -t 48:00:00 --mail-type=end --mail-user=stamal@live.unc.edu "
#baseCommand += email
baseCommand +=" --wrap=\"python3 exp.py "

# build up different arguments
# get each of the three criticality_util distributions and the three task_utils for each person

# make sure this is ordered by priority in Constants
taskUtilList = ['unilight'] # NAMED_UTILIZATIONS.keys()
periodDist = NAMED_PERIODS.keys()
csLen = CSLENGTH.keys()
coreCounts = [4,8,16,32]
#for core in Constants.NUM_PROC:
#    coreCounts.append(str(core))
#maxPeriodList = Constants.PERIOD_MAX
count = 0

# make sure critUtilList is ordered by priority
for m in Constants.NUM_PROC:
    for u in Constants.NORM_UTILS:
        for p in Constants.PACC:
            for task_util in taskUtilList:
                for period in periodDist:
                    num_res = [m//4, m//2, m, 2*m]
                    for nres in num_res:
                        for cs in csLen:
                            arg = " -m "
                            arg += str(m)
                            arg += " -t "
                            arg += period
                            arg += " -u "
                            arg += task_util
                            arg += " -c "
                            arg += cs
                            arg += " -r "
                            arg += str(nres)
                            arg += " -p "
                            arg += str(p)
                            arg += " -s "
                            arg += str(u)
                            arg += "\""
                            fullCommand = baseCommand + arg
                            print(fullCommand)
                            print(" ")
                            count += 1

print "total: ", count