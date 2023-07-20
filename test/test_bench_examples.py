import unittest
import pytest
from bencher import BenchRunCfg
from bencher.example.example_categorical import example_categorical
from bencher.example.example_floats import example_floats
from bencher.example.example_floats2D import example_floats2D
from bencher.example.example_pareto import example_pareto
from bencher.example.example_simple_cat import example_1D_cat
from bencher.example.example_simple_float import example_1D_float
from bencher.example.example_persistent import example_persistent
from bencher.example.example_float_cat import example_cat_float
from bencher.example.example_time_event import example_time_event
from bencher.example.example_float3D import example_floats3D
from bencher.example.example_float3D_cone import example_cone
from bencher.example.example_custom_sweep import example_custom_sweep
from bencher.example.example_workflow import example_floats2D_workflow, example_floats3D_workflow
from bencher.example.example_vector import example_vector
from bencher.example.example_plot_library import example_plot_library


class TestBenchExamples(unittest.TestCase):
    """The purpose of this test class is to run the example problems to make sure they don't crash.  The bencher logic is tested in the other test files test_bencher.py and test_vars.py"""

    def create_run_cfg(self) -> BenchRunCfg:
        cfg = BenchRunCfg()
        cfg.repeats = 2  # low number of repeats to reduce test time, but also test averaging and variance code
        cfg.debug = True  # reduce size of param sweep so tests are faster
        cfg.clear_cache = True
        return cfg

    def test_example_categorical(self) -> None:
        self.assertIsNotNone(example_categorical(self.create_run_cfg()))

    def test_example_floats(self) -> None:
        self.assertIsNotNone(example_floats(self.create_run_cfg()))

    def test_example_floats2D(self) -> None:
        self.assertIsNotNone(example_floats2D(self.create_run_cfg()))

    def test_example_pareto(self) -> None:
        self.assertIsNotNone(example_pareto(self.create_run_cfg()))

    def test_example_simple_cat(self) -> None:
        self.assertIsNotNone(example_1D_cat(self.create_run_cfg()))

    def test_example_simple_float(self) -> None:
        self.assertIsNotNone(example_1D_float(self.create_run_cfg()))

    def test_example_persistent(self) -> None:
        self.assertIsNotNone(example_persistent(self.create_run_cfg()))

    def test_example_cat_float(self) -> None:
        self.assertIsNotNone(example_cat_float(self.create_run_cfg()))

    def test_example_time_event(self) -> None:
        self.assertIsNotNone(example_time_event(self.create_run_cfg()))

    def test_example_float3D(self) -> None:
        self.assertIsNotNone(example_floats3D(self.create_run_cfg()))

    def test_example_cone(self) -> None:
        self.assertIsNotNone(example_cone(self.create_run_cfg()))

    def test_example_custom_sweep(self) -> None:
        self.assertIsNotNone(example_custom_sweep(self.create_run_cfg()))

    def test_example_floats2D_workflow(self) -> None:
        self.assertIsNotNone(example_floats2D_workflow(self.create_run_cfg()))

    def test_example_floats3D_workflow(self) -> None:
        self.assertIsNotNone(example_floats3D_workflow(self.create_run_cfg()))

    @pytest.mark.skip
    def test_example_vector(self) -> None:
        self.assertIsNotNone(example_vector())

    def test_plot_library(self) -> None:
        self.assertIsNotNone(example_plot_library(self.create_run_cfg()))
