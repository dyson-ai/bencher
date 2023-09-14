# from typing import Any
import dispy
# import param
import random
import numpy as np
import param

# import bencher as bch
import logging
import os, dispy
# from bencher.example.benchmark_data import AllSweepVars

print(os.path.join(os.path.dirname(dispy.__file__), 'data'))
# import bencher


# https://pycos.org/dispycos.html#examples
# https://pycos.org/dispycos.html#docker-container
# http://dispy.org/dispynode.html#containers

# class C(param.Parameterized):
# class C():
#     def __init__(self, i=0, n=0):
#         self.i = i
#         self.n = n
#         np.ones([1])
#         self.a =param.Boolean()


#     def show(self):
#         print('%s: %.2f' % (self.i, self.n))
#     def __call__(self,**kwargs) :
#         return dict(n=self.n,a=self.a)

# def setup(args):
    # import param
    # pass

def wrapper(**kwargs):    
    import param 
    from bencher.example.benchmark_data import AllSweepVars

    asv = AllSweepVars()

    return asv.__call__(**kwargs)


    # asv =AllSweepVars()
    # class BasicParam(param.Parameterized):

    #     var1 = param.Number()

    #     def __call__(self, **kwargs):
    #         var1 = kwargs.get("var1", 0)

    #         return var1+1

    # class BasicSweep(bch.ParameterizedSweep):

    #     var1 = param.Number()

    #     def __call__(self, **kwargs):
    #         var1 = kwargs.get("var1", 0)

    #         return var1+1

    # a = param.Number()
    # bch.FloatSweep()
    # import param
    # cp = CachedParamExample()  # clears cache by default
    # var1 = kwargs.get("var1", 0)
    # print(f"starting {var1}")
    # bp = BasicParam()
    # return bp.__call__(**kwargs)
    # for i in range(1000):
    #     logging.debug(i)

    # print(f"finishing {var1}")

    # result = var1 + random.uniform(0, 1)

    return var1 
    return dict(result=result)
    # # res = cp.__call__(**kwargs)
    # # return res

def wrapper_bench(**kwargs):
    from bencher.example.benchmark_data import AllSweepVars
    return AllSweepVars().__call__(**kwargs)

if __name__ == '__main__':
    import random, dispy
    # 'compute' needs definition of class C, so include in 'depends'
    # cluster = dispy.JobCluster(C.__call__, depends=[C,param,param.Parameterized])

    param_deps = [param,param.parameterized,param.parameterized.serializer]
    # bench_deps =[bencher,bencher.bencher,bencher.worker_job,bencher.utils,bencher.bench_cfg]
    # func_deps = [bch.example.benchmark_data.AllSweepVars]
    # func_deps = [BasicParam,AllSweepVars]
    func_deps =[]
    # depends =  func_deps+param_deps
    depends = param_deps
    depends =[]
    # depends =["/home/agsmith/bencher/test/run_dispy.py","/home/agsmith/bencher/test/basic_param.py"]
    # depends =  param_deps+bench_deps +func_deps


    # cluster = dispy.JobCluster(C.__call__, depends=[C])
    cluster = dispy.JobCluster(wrapper_bench,nodes=["10.51.103.13","10.50.103.17"], depends=depends)
    # cluster = dispy.JobCluster(wrapper,depends=depends)
    # cluster = dispy.JobCluster(wrapper_bench,depends=depends)


    # cluster = dispy.JobCluster(wrapper, depends=[C,param,bch,bch.SweepBase,bch.FloatSweep])
    # import functools
    # wrapped1 = functools.partial(BasicParam.__call__,BasicParam())


    # cluster = dispy.JobCluster(BasicParam.__call__, depends=depends)
    # cluster = dispy.JobCluster(wrapped1, depends=depends)




    jobs = []
    for i in range(100):
        # c = C(i, random.uniform(1, 3)) # create object of C
        # job = cluster.submit(c) # it is sent to a node for executing 'compute'

        job = cluster.submit(var_float=i/100.) # it is sent to a node for executing 'compute'


        # job.id = c # store this object for later use
        jobs.append(job)
    for job in jobs:
        res =job() # wait for job to finish
        if res is not None:
            print(res)
        else:
            logging.info(f"job id{job.id}")
            logging.info(f"result:{job.result}")
            if len(job.stdout):
                logging.info(job.stdout)
            if len(job.stderr):
                logging.warning(job.stderr)
            if len(job.exception):
                logging.critical(f"exception: { job.exception}")
            




        
        # print(res.result)
        # print(f"{job.result} : {job.stdout}")


