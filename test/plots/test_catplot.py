from bencher.plotting.plot_collection import PlotInput
from bencher.plotting.plot_types import PlotTypes
from bencher.plotting.plots.catplot import Catplot
from bencher.bench_cfg import PltCntCfg
from hypothesis import given, settings, strategies as st

from bencher.example.benchmark_data import ExampleBenchCfgOut


from .test_plots_common import TestPlotsCommon


class TestCatPlot(TestPlotsCommon):
    @settings(deadline=10000)
    @given(
        st.sampled_from(
            [PlotTypes.swarmplot, PlotTypes.barplot, PlotTypes.boxenplot, PlotTypes.violinplot]
        )
    )
    def test_plot_name(self, plot_name) -> None:
        bench_cfg = self.create_bench_cfg(plot_name)

        plt_cnt_cfg = PltCntCfg(float_cnt=0, cat_cnt=1)
        pl_in = PlotInput(bench_cfg, ExampleBenchCfgOut.param.out_cos, plt_cnt_cfg)
        cp = Catplot()
        plot_fn = getattr(cp, plot_name)
        result = plot_fn(pl_in)

        self.basic_plot_asserts(result, plot_name)
