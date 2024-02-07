import unittest
import bencher as bch
import numpy as np

from bencher.example.meta.example_meta import BenchableObject


class TestBenchResultBase(unittest.TestCase):
    def test_to_dataset(self):
        bench = BenchableObject().to_bench()

        res_repeat1 = bench.plot_sweep(
            "sweep1repeat",
            input_vars=[BenchableObject.param.float1],
            result_vars=[BenchableObject.param.distance, BenchableObject.param.sample_noise],
            run_cfg=bch.BenchRunCfg(repeats=1),
            plot=False,
        )

        res_repeat2 = bench.plot_sweep(
            "sweep2repeat",
            input_vars=[BenchableObject.param.float1],
            result_vars=[BenchableObject.param.distance, BenchableObject.param.sample_noise],
            run_cfg=bch.BenchRunCfg(repeats=2),
            plot=False,
        )

        # print(res_repeat1.to_dataset())
        # print(res_repeat1.to_hv_dataset().data)
        # print(res_repeat1.to_hv_dataset_old().data)

        # print(res_repeat1.to_dataset()["distance"].attrs)

        # print(res_repeat2.to_dataset())
        # print(res_repeat2.to_hv_dataset())
        # print(res_repeat2.to_dataset()["distance"].attrs)

        self.assertEqual(
            res_repeat1.to_dataset()["distance"].attrs, res_repeat2.to_dataset()["distance"].attrs
        )

        # bm.__call__(float_vars=1, sample_with_repeats=1)

    def test_select_level(self):

        class TestBench(bch.ParametrizedSweep):
            float_var = bch.FloatSweep(default=0, bounds=[0, 5])
            cat_var = bch.StringSweep(["a", "b", "c", "d", "e"])

        bench = BenchableObject().to_bench()

        res = bench.plot_sweep(
            input_vars=["float_var", "cat_var"],
            run_cfg=bch.BenchRunCfg(level=4)
            plot=False,
        )

        ds_raw = res.to_dataset()

        np.testing.assert_array_equal(ds_raw.coords["float_var"].to_numpy(),np.array([0,1,2,3,4,5]))



