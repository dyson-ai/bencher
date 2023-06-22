import unittest
import panel as pn

from bencher.plotting.plot_collection import PlotInput
from bencher.plotting.plot_types import PlotTypes
from bencher.plotting.plots.tables import Tables
from bencher.bench_cfg import PltCntCfg
import bencher as bch
from bencher.example.benchmark_data import ExampleBenchCfgIn, ExampleBenchCfgOut, bench_function
from hypothesis import given, settings, strategies as st


class TestCatPlot(unittest.TestCase):
    @settings(deadline=10000)
    @given(
        st.sampled_from(
            [
                PlotTypes.dataframe_flat,
                PlotTypes.dataframe_mean,
                PlotTypes.dataframe_multi_index,
                PlotTypes.xarray,
            ]
        )
    )
    def test_plot_name(self, plot_name) -> None:
        bencher = bch.Bench("test_tables", bench_function, ExampleBenchCfgIn)

        bench_cfg = bencher.plot_sweep(
            title="Test Cat Plots",
            input_vars=[ExampleBenchCfgIn.param.postprocess_fn],
            const_vars=[(ExampleBenchCfgIn.param.noisy, True)],
            result_vars=[ExampleBenchCfgOut.param.out_cos],
            plot_lib=bch.PlotLibrary.none().add(plot_name),
            run_cfg=bch.BenchRunCfg(auto_plot=False),
        )

        plt_cnt_cfg = PltCntCfg(float_cnt=0, cat_cnt=1)
        pl_in = PlotInput(bench_cfg, ExampleBenchCfgOut.param.out_cos, plt_cnt_cfg)
        cp = Tables()
        plot_fn = getattr(cp, plot_name)
        result = plot_fn(pl_in)
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], pn.viewable.Viewable)
        self.assertEqual(result[0].name, plot_name)
