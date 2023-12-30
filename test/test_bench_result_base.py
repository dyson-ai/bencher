import pytest
import unittest
from hypothesis import given, settings, strategies as st
import bencher as bch
from datetime import datetime

from strenum import StrEnum
from enum import auto
from typing import List
from param import Parameter
from itertools import combinations
from bencher.example.example_meta import BenchMeta, BenchableObject


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
