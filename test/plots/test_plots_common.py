import unittest

import panel as pn

import bencher as bch
from bencher.example.benchmark_data import ExampleBenchCfgIn, ExampleBenchCfgOut, bench_function


class TestPlotsCommon(unittest.TestCase):
    def create_bench_cfg(self, plot_name: str) -> bch.BenchCfg:
        """Given a plot name, run a sweep and plot with that plotting function

        Args:
            plot_name (str): name of the plot to use

        Returns:
            BenchCfg: Results with plots
        """
        bencher = bch.Bench("test_catplot", bench_function, ExampleBenchCfgIn)
        return bencher.plot_sweep(
            title="Test Cat Plots",
            input_vars=[ExampleBenchCfgIn.param.postprocess_fn],
            const_vars=[(ExampleBenchCfgIn.param.noisy, True)],
            result_vars=[ExampleBenchCfgOut.param.out_cos],
            plot_lib=bch.PlotLibrary.none().add(plot_name),
            run_cfg=bch.BenchRunCfg(auto_plot=False),
        )

    def basic_plot_asserts(self, result: bch.BenchCfg, plot_name: str) -> None:
        """Check that the expected plots are generated

        Args:
            result (bch.BenchCfg): bench result to check
            plot_name (str): expected name of the plot
        """

        self.assertIsInstance(result, pn.viewable.Viewable)
        self.assertEqual(result.name, plot_name)
