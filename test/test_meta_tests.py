import unittest
import bencher as bch
from bencher.example.example_floats2D import example_floats2D
from bencher.example.example_pareto import example_pareto
from bencher.example.example_simple_cat import example_1D_cat
from bencher.example.example_simple_float import example_1D_float
from bencher.example.example_float_cat import run_example_float_cat
from bencher.example.example_time_event import run_example_time_event
from bencher.example.example_float3D import example_floats3D

from bencher.example.example_custom_sweep import example_custom_sweep
from bencher.example.example_workflow import example_floats2D_workflow, example_floats3D_workflow
from bencher.example.example_holosweep import example_holosweep
from bencher.example.example_holosweep_tap import example_holosweep_tap

from bencher.example.optuna.example_optuna import optuna_rastrigin
from bencher.example.example_sample_cache import example_sample_cache
from bencher.example.example_strings import example_strings
from bencher.example.example_image import example_image
from bencher.example.example_video import example_video
from bencher.example.example_meta_levels import example_meta_levels
from bencher.example.example_meta import BenchMeta, BenchableObject
import os
import math
import numpy as np

# shelved
# from bencher.example.shelved.example_float2D_scatter import example_floats2D_scatter
# from bencher.example.shelved.example_float3D_cone import example_cone
from dataclasses import dataclass


@dataclass
class V3:
    x: float
    y: float
    z: float
    distance: float

    def __call__(self):
        self.distance = math.pow(
            np.linalg.norm(np.array([self.float1, self.float2, self.float3])), 2
        )


def distance(x, y, z):
    return math.pow(np.linalg.norm(np.array([x, y, z])), 2)


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

        # print(res1.to_dataset(bch.ReduceType.SQUEEZE))
        # print(res2.to_dataset(bch.ReduceType.REDUCE))

        res1_ds = res1.to_dataset(bch.ReduceType.SQUEEZE)
        res2_ds = res2.to_dataset(bch.ReduceType.REDUCE)

        self.assertFalse(res1_ds.identical(res2_ds),"should not be equal because of std_dev column")

        res2_ds = res2_ds.drop_vars("distance_std")
        res2_ds = res2_ds.drop_vars("sample_noise_std")

        print(res1_ds)
        print(res2_ds)

        print(res1_ds["distance"].attrs)
        print(res2_ds["distance"].attrs)

        self.assertTrue(res1_ds["distance"].attrs.equals(res2_ds),"should be equal because of std_dev column")

        
        self.assertTrue(res1_ds.equals(res2_ds),"should be equal because of std_dev column")

        self.assertTrue(res1_ds.identical(res2_ds),"should be equal because of std_dev column")



        # self.assertTrue(
        #     res1.to_dataset(bch.ReduceType.SQUEEZE).identical(
        #         res2.to_dataset(bch.ReduceType.REDUCE)
        #     ),
        #     "both have repeats removed so should be equal again",
        # )

        self.assertTrue(
            res1.to_dataset().identical(res2.to_dataset()),
            "passing no arguments should select correct reduction types where both have repeats removed so should be equal again",
        )
