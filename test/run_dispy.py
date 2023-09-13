# from typing import Any
import dispy
# import param
import random
import numpy as np
import param

import bencher as bch
import logging

import os, dispy
print(os.path.join(os.path.dirname(dispy.__file__), 'data'))

# https://pycos.org/dispycos.html#examples
# https://pycos.org/dispycos.html#docker-container
# http://dispy.org/dispynode.html#containers

# class C(param.Parameterized):
class C():
    def __init__(self, i=0, n=0):
        self.i = i
        self.n = n
        np.ones([1])
        self.a =param.Boolean()


    def show(self):
        print('%s: %.2f' % (self.i, self.n))
    def __call__(self,**kwargs) :
        return dict(n=self.n,a=self.a)



class BasicParam(param.Parameterized):

    var1 = param.Number()

    def __call__(self, **kwargs):
        var1 = kwargs.get("var1", 0)

        return var1


def wrapper(**kwargs):

    # a = param.Number()
    # bch.FloatSweep()
    # cp = CachedParamExample()  # clears cache by default
    var1 = kwargs.get("var1", 0)
    # print(f"starting {var1}")
    # bp = BasicParam()
    # for i in range(1000):
    #     logging.debug(i)

    # print(f"finishing {var1}")

    # result = var1 + random.uniform(0, 1)

    return var1 
    return dict(result=result)
    # # res = cp.__call__(**kwargs)
    # # return res



if __name__ == '__main__':
    import random, dispy
    # 'compute' needs definition of class C, so include in 'depends'
    # cluster = dispy.JobCluster(C.__call__, depends=[C,param,param.Parameterized])

    # cluster = dispy.JobCluster(C.__call__, depends=[C])
    cluster = dispy.JobCluster(wrapper, depends=[C])
    # cluster = dispy.JobCluster(wrapper, depends=[C,param,bch,bch.SweepBase,bch.FloatSweep])


    jobs = []
    for i in range(10):
        # c = C(i, random.uniform(1, 3)) # create object of C
        # job = cluster.submit(c) # it is sent to a node for executing 'compute'

        job = cluster.submit(var1=i) # it is sent to a node for executing 'compute'


        # job.id = c # store this object for later use
        jobs.append(job)
    for job in jobs:
        res =job() # wait for job to finish
        print(res)
        # print(res.result)
        # print(f"{job.result} : {job.stdout}")

        # print(f"{job.id.i} {job.result} : {job.stdout}")

