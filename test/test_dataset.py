import unittest
import bencher as bch
from bencher.plotting.plot_filter import VarRange, PlotFilter
from hypothesis import given, strategies as st


class ExSweep(bch.ParametrizedSweep):
    """A class containing all the sweep types, This class is used for unit testing how the configuration classes are serialised and hashed"""

    float1 = bch.FloatSweep(bounds=(0, 10), units="m/s")
    float2 = bch.FloatSweep(bounds=(0, 10), units="m/s")

    result = bch.ResultVar()

    def __call__(self, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)
        self.result = self.float1 + self.float2
        return self.get_results_values_as_dict()


class TestDataset(unittest.TestCase):
    def test_matches_zero(self) -> None:

        bench = bch.Bench("test_dataset", ExSweep())

        bench_cfg = bench.setup_bench_cfg(
            "test_dataset", input_vars=[ExSweep.param.float1, ExSweep.param.float2]
        )

        bench_cfg = bench.setup_dataset(bench_cfg=bench_cfg)

        # bench.plot_sweep()

        # bench_cfg = bch.BenchCfg()
        # bench_cfg.

        bench_cfg, function_inputs, dims_name = bench.setup_dataset(bench_cfg)

        print(function_inputs)
        print(dims_name)

    # def test_matches_upto(self) -> None:
    #     var_range = VarRange(0, 1)
    #     # self.assertFalse(zero_case.matches(-1))
    #     self.assertTrue(var_range.matches(0))
    #     self.assertTrue(var_range.matches(1))
    #     self.assertFalse(var_range.matches(2))
