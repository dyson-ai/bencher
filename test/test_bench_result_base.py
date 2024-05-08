import unittest
import bencher as bch
import numpy as np

from bencher.example.meta.example_meta import BenchableObject


class TestBench(bch.ParametrizedSweep):
    float_var = bch.FloatSweep(default=0, bounds=[0, 4])
    cat_var = bch.StringSweep(["a", "b", "c", "d", "e"])
    result = bch.ResultVar()

    def __call__(self, **kwargs):
        self.result = 1
        return super().__call__()


class TestBenchResultBase(unittest.TestCase):
    def test_to_dataset(self):
        bench = BenchableObject().to_bench()

        res_repeat1 = bench.plot_sweep(
            "sweep1repeat",
            input_vars=[BenchableObject.param.float1],
            result_vars=[BenchableObject.param.distance, BenchableObject.param.sample_noise],
            run_cfg=bch.BenchRunCfg(repeats=1),
            plot_callbacks=False,
        )

        res_repeat2 = bench.plot_sweep(
            "sweep2repeat",
            input_vars=[BenchableObject.param.float1],
            result_vars=[BenchableObject.param.distance, BenchableObject.param.sample_noise],
            run_cfg=bch.BenchRunCfg(repeats=2),
            plot_callbacks=False,
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
        bench = TestBench().to_bench()

        res = bench.plot_sweep(
            input_vars=["float_var", "cat_var"],
            run_cfg=bch.BenchRunCfg(level=4),
            plot_callbacks=False,
        )

        def asserts(ds, expected_float, expected_cat):
            np.testing.assert_array_equal(
                ds.coords["float_var"].to_numpy(), np.array(expected_float, dtype=float)
            )
            np.testing.assert_array_equal(ds.coords["cat_var"].to_numpy(), np.array(expected_cat))

        ds_raw = res.to_dataset()
        asserts(ds_raw, [0, 1, 2, 3, 4], ["a", "b", "c", "d", "e"])

        ds_filtered_all = res.select_level(ds_raw, 2)
        asserts(ds_filtered_all, [0, 4], ["a", "e"])

        ds_filtered_types = res.select_level(ds_raw, 2, float)
        asserts(ds_filtered_types, [0, 4], ["a", "b", "c", "d", "e"])

        ds_filtered_names = res.select_level(ds_raw, 2, exclude_names="cat_var")
        asserts(ds_filtered_names, [0, 4], ["a", "b", "c", "d", "e"])
