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
            result_vars=[BenchableObject.param.distance],
            run_cfg=bch.BenchRunCfg(repeats=1),
        )

        res_repeat2 = bench.plot_sweep(
            "sweep2repeat",
            input_vars=[BenchableObject.param.float1],
            result_vars=[BenchableObject.param.distance],
            run_cfg=bch.BenchRunCfg(repeats=2),
        )

        # print(res_repeat1.to_dataset())
        # print(res_repeat1.to_dataset()["distance"].attrs)

        self.assertEqual(
            res_repeat1.to_dataset()["distance"].attrs, res_repeat2.to_dataset()["distance"].attrs
        )

        # self.assertTrue(False)

        # bm.__call__(float_vars=1, sample_with_repeats=1)
