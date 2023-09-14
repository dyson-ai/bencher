# from typing import Any
import dispy
# import param
import random
import numpy as np
import param

# import bencher as bch
import logging
import os, dispy

# https://pycos.org/dispycos.html#examples
# https://pycos.org/dispycos.html#docker-container
# http://dispy.org/dispynode.html#containers

def wrapper(**kwargs):
    from bencher.example.benchmark_data import AllSweepVars
    return AllSweepVars().__call__(**kwargs)

if __name__ == '__main__':
    import random, dispy
    # 'compute' needs definition of class C, so include in 'depends'
    # cluster = dispy.JobCluster(C.__call__, depends=[C,param,param.Parameterized])

    # param_deps = [param,param.parameterized,param.parameterized.serializer]
    # bench_deps =[bencher,bencher.bencher,bencher.worker_job,bencher.utils,bencher.bench_cfg]
    # func_deps = [bch.example.benchmark_data.AllSweepVars]
    # func_deps = [BasicParam,AllSweepVars]
    # func_deps =[]
    # depends =  func_deps+param_deps
    # depends = param_deps
    depends =[]
    # depends =["/home/agsmith/bencher/test/run_dispy.py","/home/agsmith/bencher/test/basic_param.py"]
    # depends =  param_deps+bench_deps +func_deps


    # cluster = dispy.JobCluster(C.__call__, depends=[C])
    cluster = dispy.JobCluster(wrapper,nodes=["10.50.103.17","10.50.103.16","10.51.103.13"], depends=depends,cleanup=True)
    # sudo ufw allow 9701
    # sudo ufw allow 9700



    # cluster = dispy.JobCluster(wrapper_bench,nodes=["10.50.103.17"], depends=depends,cleanup=False)

    # cluster = dispy.JobCluster(wrapper,depends=depends)
    # cluster = dispy.JobCluster(wrapper_bench,depends=depends)


    # cluster = dispy.JobCluster(wrapper, depends=[C,param,bch,bch.SweepBase,bch.FloatSweep])
    # import functools
    # wrapped1 = functools.partial(BasicParam.__call__,BasicParam())


    # cluster = dispy.JobCluster(BasicParam.__call__, depends=depends)
    # cluster = dispy.JobCluster(wrapped1, depends=depends)




    jobs = []
    for i in range(300):
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


