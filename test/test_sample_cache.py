import unittest
import bencher as bch
from bencher.example.example_sample_cache import UnreliableClass


class TestSampleCache(unittest.TestCase):
    def call_bencher(self, bencher, run_cfg):
        bencher.plot_sweep(
            title="Example Crashy Function with the sample_cache",
            input_vars=[UnreliableClass.param.input_val],
            result_vars=[
                UnreliableClass.param.return_value,
                UnreliableClass.param.trigger_crash,
            ],
            description="""This example shows how to use the use_sample_cache option to deal with unreliable functions and to continue benchmarking using previously calculated results even if the code crashing during the run""",
            run_cfg=run_cfg,
            post_description="The input_val vs return value graph is a straigh line as expected and there is no record of the fact the benchmark crashed halfway through. The second graph shows that for values >1 the trigger_crash value had to be 0 in order to proceed",
        )

    def test_sample_cache(self):
        """The sample cache function needs to be run twice because the first time run can pass when there is no cache, but will fail the second time when a cache exists"""
        self.sample_cache()
        self.sample_cache()

    def sample_cache(self):
        run_cfg = bch.BenchRunCfg()
        run_cfg.repeats = 1

        run_cfg.clear_sample_cache = True
        run_cfg.use_sample_cache = True  # this will store the result of of every call

        instance = UnreliableClass()
        instance.trigger_crash = True

        bencher = bch.Bench("example_sample_cache", instance.crashy_fn)

        with self.assertRaises(RuntimeError):
            self.call_bencher(bencher, run_cfg)

        self.assertEqual(bencher.worker_wrapper_call_count, 3)
        self.assertEqual(bencher.worker_fn_call_count, 3)
        self.assertEqual(bencher.worker_cache_call_count, 0)

        run_cfg.clear_sample_cache = False
        instance.trigger_crash = False

        bencher.clear_call_counts()
        self.call_bencher(bencher, run_cfg)

        self.assertEqual(bencher.worker_wrapper_call_count, 4)
        self.assertEqual(bencher.worker_fn_call_count, 2)
        self.assertEqual(bencher.worker_cache_call_count, 2)

        run_cfg.repeats = 2

        bencher.clear_call_counts()
        self.call_bencher(bencher, run_cfg)

        self.assertEqual(bencher.worker_wrapper_call_count, 8)
        self.assertEqual(bencher.worker_fn_call_count, 4)
        self.assertEqual(bencher.worker_cache_call_count, 4)

        # create a new benchmark and clear the cache (for this new benchmark only)

        run_cfg.clear_sample_cache = True
        bencher.clear_call_counts()
        bencher.plot_sweep(
            title="new benchmark", result_vars=[UnreliableClass.param.return_value], run_cfg=run_cfg
        )

        self.assertEqual(bencher.worker_wrapper_call_count, 2)
        self.assertEqual(bencher.worker_fn_call_count, 2)
        self.assertEqual(bencher.worker_cache_call_count, 0)

        # check that the previous benchmark still has the cached values, and they were not cleared by clearing the sample cache of an unrelated benchmark

        run_cfg.clear_sample_cache = False
        bencher.clear_call_counts()
        self.call_bencher(bencher, run_cfg)

        self.assertEqual(bencher.worker_wrapper_call_count, 8)
        self.assertEqual(bencher.worker_fn_call_count, 0)
        self.assertEqual(bencher.worker_cache_call_count, 8)
