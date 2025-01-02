import unittest
import bencher as bch
from bencher.example.example_floats2D import example_floats2D
from bencher.example.example_pareto import example_pareto
from bencher.example.example_simple_cat import example_1D_cat
from bencher.example.example_simple_float import example_1D_float
from bencher.example.example_simple_float2d import example_2D_float
from bencher.example.example_consts import example_2D_float_const
from bencher.example.example_float_cat import run_example_float_cat
from bencher.example.example_time_event import run_example_time_event
from bencher.example.example_float3D import example_floats3D

from bencher.example.example_custom_sweep import example_custom_sweep
from bencher.example.example_custom_sweep2 import example_custom_sweep2
from bencher.example.example_levels2 import example_levels2
from bencher.example.example_workflow import (
    example_floats2D_workflow,
    example_floats3D_workflow,
)
from bencher.example.example_holosweep import example_holosweep
from bencher.example.example_holosweep_tap import example_holosweep_tap

from bencher.example.example_dataframe import example_dataset
from bencher.example.optuna.example_optuna import optuna_rastrigin
from bencher.example.example_sample_cache import example_sample_cache
from bencher.example.example_strings import example_strings
from bencher.example.example_image import example_image, example_image_vid
from bencher.example.example_video import example_video
from bencher.example.example_filepath import example_filepath
from bencher.example.meta.example_meta import example_meta
from bencher.example.example_docs import example_docs

import os


class TestReport(unittest.TestCase):
    """The purpose of this test class is to run the example problems to make sure they don't crash.  The bencher logic is tested in the other test files test_bencher.py and test_vars.py"""


    def test_example_floats2D_report(self) -> None:
        example_floats2D(bch.BenchRunCfg(level=2).report.save()
