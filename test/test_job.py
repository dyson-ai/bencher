import unittest
import bencher as bch
import random
from bencher.job import JobFunctionCache, JobCache, Job

from hypothesis import given, strategies as st, settings
import dispy

class CachedParamExample(bch.ParametrizedSweep):
    var1 = bch.FloatSweep(default=0, bounds=[0, 100000])
    var2 = bch.IntSweep(default=10, bounds=[0, 10])

    result = bch.ResultVar()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        self.result = self.var1 + self.var2 + random.uniform(0, 1)
        return self.get_results_values_as_dict()

    def call_args(self, *args, **kwargs):
        return self, __call__(**kwargs)


class TestJob(unittest.TestCase):
    @settings(deadline=500)
    @given(st.booleans())
    def test_basic(self, parallel):
        cp = CachedParamExample()  # clears cache by default

        jc = JobFunctionCache(cp.__call__, parallel=parallel, cache_name="test_cache")
        jc.clear()

        res1 = jc.call(var1=1).result()
        res2 = jc.call(var1=1).result()
        res3 = jc.call(var1=2).result()
        res4 = jc.call(var2=2).result()

        # will only be equal if cache is used because of the randomness
        self.assertEqual(res1["result"], res2["result"])
        self.assertNotEqual(res1["result"], res3["result"], f"{res1}")
        self.assertNotEqual(res1["result"], res4["result"], f"{res1}")

        # create new class, make sure it has the same results
        cp2 = CachedParamExample()
        jc2 = JobFunctionCache(cp2.__call__, parallel=parallel, cache_name="test_cache")
        res1cp2 = jc2.call(var1=1).result()
        self.assertEqual(res1["result"], res1cp2["result"])

        # create cache with a different name and check it does not have the same results
        cp3 = CachedParamExample()
        jc3 = JobFunctionCache(cp3.__call__, parallel=parallel, cache_name="test_cache2")
        res1cp3 = jc3.call(var1=1).result()
        self.assertNotEqual(res1["result"], res1cp3["result"])

    @settings(deadline=500)
    @given(st.booleans())
    def test_overwrite(self, parallel):
        cp = CachedParamExample()  # clears cache by default

        jc = JobFunctionCache(cp.__call__, parallel=parallel, cache_name="test_cache1")
        jc.clear()

        res1 = jc.call(var1=1).result()

        self.assertEqual(jc.worker_wrapper_call_count, 1)
        self.assertEqual(jc.worker_cache_call_count, 0)
        self.assertEqual(jc.worker_fn_call_count, 1)

        jc.clear_call_counts()
        res2 = jc.call(var1=1).result()

        self.assertEqual(jc.worker_wrapper_call_count, 1)
        self.assertEqual(jc.worker_cache_call_count, 1)
        self.assertEqual(jc.worker_fn_call_count, 0)

        self.assertEqual(res1["result"], res2["result"])

        jc.clear_call_counts()
        jc.overwrite = True
        res3 = jc.call(var1=1).result()
        self.assertEqual(jc.worker_wrapper_call_count, 1)
        self.assertEqual(jc.worker_cache_call_count, 0)
        self.assertEqual(jc.worker_fn_call_count, 1)

        self.assertNotEqual(res1["result"], res3["result"], f"{res1}")

    @settings(deadline=1000)
    @given(st.booleans())
    def test_bench_runner_parallel(self, parallel):
        run_cfg = bch.BenchRunCfg()
        run_cfg.overwrite_sample_cache = True
        run_cfg.parallel = parallel
        bench_run = bch.BenchRunner("test_bench_runner", run_cfg=run_cfg)

        bench_run.add_bench(CachedParamExample())

        bench_run.run(level=2)


import param
import logging
from joblib import Memory, Parallel, delayed


class BasicParam(param.Parameterized):

    var1 = param.Number()

    def __call__(self, **kwargs):
        var1 = kwargs.get("var1", 0)

        return var1


def wrapper(**kwargs):

    # cp = CachedParamExample()  # clears cache by default
    var1 = kwargs.get("var1", 0)
    print(f"starting {var1}")
    bp = BasicParam()
    for i in range(1000000):
        logging.debug(i)

    print(f"finishing {var1}")

    result = var1 + random.uniform(0, 1)
    return 1
    return dict(result=result)
    # res = cp.__call__(**kwargs)
    # return res



def run_dispy():
    # executed on client only; variables created below, including modules imported,
    # are not available in job computations
    import dispy, random
    # distribute 'compute' to nodes; in this case, 'compute' does not have
    # any dependencies to run on nodes
    # cluster = dispy.JobCluster(wrapper,depends=["/workspaces/bencher/test/test_job.py"])
    cluster = dispy.JobCluster(wrapper,depends=[param,BasicParam])
    # run 'compute' with 20 random numbers on available CPUs
    jobs = []
    for i in range(20):
        job = cluster.submit(var1=random.randint(5,20))
        jobs.append(job)
    # cluster.wait() # waits until all jobs finish
    for job in jobs:
        result = job() # waits for job to finish and returns results

        print(result)
        # print('%s executed job %s at %s with %s' % (host, job.id, job.start_time))
        # other fields of 'job' that may be useful:
        # job.stdout, job.stderr, job.exception, job.ip_addr, job.end_time
    cluster.print_status()  # shows which nodes executed how many jobs etc.

if __name__ == "__main__":
    import os
    print(os.path.join(os.path.dirname(dispy.__file__), 'data'))
    run_dispy()
    exit()

    location = "cachedir/joblib"
    memory = Memory(location, verbose=0)
    memory.clear()
    # cp = CachedParamExample()
    # costly_compute_cached = memory.cache(cp.__call__)
    costly_compute_cached = memory.cache(wrapper)

    # costly_compute_cached = memory.cache(BasicParam.__call__)

        # for i in range(100000):

    results = Parallel(n_jobs=-2, return_as="generator")(
        delayed(costly_compute_cached)(**dict(var1=i)) for i in range(1000)
    )

        print("collecting results")
    for r in results:
            print(r)
    else:
        jc = JobCache(parallel=True, cache_name="test_cache")
        jc.clear()

        futures = []
        for i in range(100000):
            futures.append(jc.add_job(Job(i, wrapper, job_args=dict(var1=i))))

        for f in futures:
            print(f.result())

    # TestJob().test_bench_runner_parallel(True).report.show()
