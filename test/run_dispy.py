# from typing import Any
import dispy

# import param
import random
import numpy as np
import param

import bencher as bch
import logging
import os, dispy


from bencher.example.benchmark_data import AllSweepVars

# https://pycos.org/dispycos.html#examples
# https://pycos.org/dispycos.html#docker-container
# http://dispy.org/dispynode.html#containers


def wrapper(**kwargs):
    from bencher.example.benchmark_data import AllSweepVars

    return AllSweepVars().__call__(**kwargs)


def dispy_wrapper(**kwargs):
    

if __name__ == "__main__":
    import random, dispy

    # func_deps = [BasicParam,AllSweepVars]
    depends = []
    nodes = []
    #  nodes=["10.50.103.17", "10.50.103.16", "10.51.103.13"]
    cluster = dispy.JobCluster(wrapper, nodes=nodes, depends=depends)

    run_cfg = bch.BenchRunCfg
    bench = bch.Bench("all_vars", wrapper)
    bench.plot_sweep("remote", [AllSweepVars.param.var_float])
    # bench.report.show()

    jobs = []
    for i in range(20):
        # c = C(i, random.uniform(1, 3)) # create object of C
        # job = cluster.submit(c) # it is sent to a node for executing 'compute'

        job = cluster.submit(var_float=i / 100.0)  # it is sent to a node for executing 'compute'

        # job.id = c # store this object for later use
        jobs.append(job)
    for job in jobs:
        res = job()  # wait for job to finish
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
