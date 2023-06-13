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
        run_cfg = bch.BenchRunCfg()
        run_cfg.repeats = 1

        run_cfg.use_sample_cache = True  # this will store the result of of every call
        run_cfg.clear_sample_cache = True

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

        bencher.worker_wrapper_call_count = 0
        bencher.worker_fn_call_count = 0
        bencher.worker_cache_call_count = 0
        self.call_bencher(bencher, run_cfg)

        self.assertEqual(bencher.worker_wrapper_call_count, 4)
        self.assertEqual(bencher.worker_fn_call_count, 2)
        self.assertEqual(bencher.worker_cache_call_count, 2)

        # example_sample_cache(run_cfg, trigger_crash=False)

        run_cfg.repeats = 2

        bencher.worker_wrapper_call_count = 0
        bencher.worker_fn_call_count = 0
        bencher.worker_cache_call_count = 0
        self.call_bencher(bencher, run_cfg)

        self.assertEqual(bencher.worker_wrapper_call_count, 8)
        self.assertEqual(bencher.worker_fn_call_count, 4)
        self.assertEqual(bencher.worker_cache_call_count, 4)

        # example_sample_cache(run_cfg, trigger_crash=False).plot()
