import unittest
import bencher as bch
import random
from bencher.job import Job,JobCache,JobFunctionCache

from hypothesis import given, settings, strategies as st


class CachedParamExample(bch.CachedParams):
    var1 = bch.FloatSweep(default=0, bounds=[0, 10])
    var2 = bch.IntSweep(default=10, bounds=[0, 10])

    result = bch.ResultVar()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        self.result = self.var1 + self.var2 + random.uniform(0, 1)
        return self.get_results_values_as_dict()


class TestJob(unittest.TestCase):

    @given(st.booleans())
    def test_basic(self,parallel):
        cp = CachedParamExample()  # clears cache by default

        jc = JobFunctionCache(cp.__call__,parallel=parallel,cache_name="test_cache")        
        jc.clear_cache()

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
        jc2 = JobFunctionCache(cp.__call__,parallel=parallel,cache_name="test_cache")   
        res1cp2 = jc2.call(var1=1).result()
        self.assertEqual(res1["result"], res1cp2["result"])

        # create cache with a different name and check it does not have the same results
        cp3 = CachedParamExample()
        jc3 = JobFunctionCache(cp.__call__,parallel=parallel,cache_name="test_cache2")   
        res1cp3 = jc3.call(var1=1).result()
        self.assertNotEqual(res1["result"], res1cp3["result"])
