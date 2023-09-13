# from typing import Any
import dispy
# import param
import random
import logging
# class BasicParam(param.Parameterized):

#     var1 = param.Number()

#     def __call__(self, **kwargs):
#         var1 = kwargs.get("var1", 0)

#         return var1


def wrapper(**kwargs):

    # cp = CachedParamExample()  # clears cache by default
    var1 = kwargs.get("var1", 0)
    print(f"starting {var1}")
    # bp = BasicParam()
    for i in range(1000):
        logging.debug(i)

    print(f"finishing {var1}")

    result = var1 + random.uniform(0, 1)
    return 1
    return dict(result=result)
    # res = cp.__call__(**kwargs)
    # return res



# def run_dispy():
#     # executed on client only; variables created below, including modules imported,
#     # are not available in job computations
#     import dispy, random
#     # distribute 'compute' to nodes; in this case, 'compute' does not have
#     # any dependencies to run on nodes
#     # cluster = dispy.JobCluster(wrapper,depends=["/workspaces/bencher/test/test_job.py"])
#     cluster = dispy.JobCluster(wrapper)
#     # cluster = dispy.JobCluster(wrapper,depends=[param,BasicParam])
#     # run 'compute' with 20 random numbers on available CPUs
#     jobs = []
#     for i in range(20):
#         job = cluster.submit(var1=random.randint(5,20))
#         jobs.append(job)
#     # cluster.wait() # waits until all jobs finish
#     for job in jobs:
#         result = job() # waits for job to finish and returns results

#         print(result)
#         # print('%s executed job %s at %s with %s' % (host, job.id, job.start_time))
#         # other fields of 'job' that may be useful:
#         # job.stdout, job.stderr, job.exception, job.ip_addr, job.end_time
#     cluster.print_status()  # shows which nodes executed how many jobs etc.

# if __name__ == "__main__":
#     import os
#     print(os.path.join(os.path.dirname(dispy.__file__), 'data'))
#     run_dispy()
    

class C():
    def __init__(self, i=0, n=0):
        self.i = i
        self.n = n

    def show(self):
        print('%s: %.2f' % (self.i, self.n))
    def __call__(self,**kwargs) :
        return dict(n=self.n)

if __name__ == '__main__':
    import random, dispy
    # 'compute' needs definition of class C, so include in 'depends'
    cluster = dispy.JobCluster(C.__call__, depends=[C])
    jobs = []
    for i in range(10):
        c = C(i, random.uniform(1, 3)) # create object of C
        job = cluster.submit(c) # it is sent to a node for executing 'compute'
        job.id = c # store this object for later use
        jobs.append(job)
    for job in jobs:
        res =job() # wait for job to finish
        print(res)
        # print(res.result)
        # print(f"{job.id.i} {job.result} : {job.stdout}")