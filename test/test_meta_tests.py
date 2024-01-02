import unittest
import bencher as bch
from bencher.example.meta.example_meta import BenchableObject


class TestBenchMeta(unittest.TestCase):
    def test_repeats_equal(self):
        # bench = bch.Bench("meta", BenchMeta())

        bench = bch.Bench("bench", BenchableObject())

        res1 = bench.plot_sweep(
            "repeats", input_vars=[BenchableObject.param.float1], run_cfg=bch.BenchRunCfg(repeats=1)
        )

        res1_eq = bench.plot_sweep(
            "repeats", input_vars=[BenchableObject.param.float1], run_cfg=bch.BenchRunCfg(repeats=1)
        )

        res2 = bench.plot_sweep(
            "repeats", input_vars=[BenchableObject.param.float1], run_cfg=bch.BenchRunCfg(repeats=2)
        )

        self.assertTrue(
            res1.to_dataset(bch.ReduceType.NONE).identical(res1_eq.to_dataset(bch.ReduceType.NONE)),
            "created with identical settings so should be equal",
        )

        self.assertFalse(
            res1.to_dataset(bch.ReduceType.NONE).identical(res2.to_dataset(bch.ReduceType.NONE)),
            "different number of repeats so should not be equal",
        )

        res1_ds = res1.to_dataset(bch.ReduceType.SQUEEZE)
        res2_ds = res2.to_dataset(bch.ReduceType.REDUCE)

        self.assertFalse(
            res1_ds.identical(res2_ds), "should not be equal because of std_dev column"
        )

        res2_ds = res2_ds.drop_vars("distance_std")
        res2_ds = res2_ds.drop_vars("sample_noise_std")

        print(res1_ds)
        print(res2_ds)
        print(res1_ds["distance"].attrs)
        print(res2_ds["distance"].attrs)

        self.assertTrue(
            res1_ds.equals(res2_ds), "should be equal because of removed std_dev column"
        )

        self.assertTrue(
            res1_ds.identical(res2_ds), "should be equal because of removed std_dev column"
        )
