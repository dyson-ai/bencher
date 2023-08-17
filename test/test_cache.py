import unittest
import bencher as bch
import random


class CachedParamExample(bch.CachedSweep):
    var1 = bch.FloatSweep(default=0, bounds=[0, 10])
    var2 = bch.IntSweep(default=10, bounds=[0, 10])

    result = bch.ResultVar()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        self.result = self.var1 + self.var2 + random.uniform(0, 1)
        return self.get_results_values_as_dict()


class TestCache(unittest.TestCase):
    def test_basic(self):
        cp = CachedParamExample()  # clears cache by default

        res1 = cp.call_cached(var1=1)
        res2 = cp.call_cached(var1=1)
        res3 = cp.call_cached(var1=2)
        res4 = cp.call_cached(var1=1, var2=10)  # calling with default value is the same
        res5 = cp.call_cached(var2=10, var1=1)  # calling with default value is the same

        # will only be equal if cache is used because of the randomness
        self.assertEqual(res1["result"], res2["result"])

        self.assertEqual(res1["result"], res4["result"])

        self.assertEqual(res4["result"], res5["result"])

        # will not be equal because called with different args
        self.assertNotEqual(res1["result"], res3["result"], f"{res1}")

        # create new class, make sure it has the same results
        cp2 = CachedParamExample(clear_cache=False)

        res1cp2 = cp2.call_cached(var1=1)

        self.assertEqual(res1["result"], res1cp2["result"])


if __name__ == "__main__":
    print(CachedParamExample().call_cached())
    # TestCache().test_basic()
