import unittest
from bencher.plotting.plot_filter import VarRange, PlotFilter
from hypothesis import given, strategies as st

from bencher.plotting.plot_collection import PlotInput
from bencher.plotting.plot_types import PlotTypes
from bencher.plotting.plot_library import PlotLibrary
from bencher.plotting.plots.catplot import CatPlot
from bencher.bench_cfg import BenchCfg, PltCntCfg
from bencher.bench_vars import ParametrizedSweep
import panel as pn


class TestCatPlot(unittest.TestCase):
    @given(st.sampled_from([PlotTypes.swarmplot]))
    def test_plot_name1(self, plot_name):
        cp = Catplot()
        bench_cfg = BenchCfg()
        rv = ParametrizedSweep()
        plt_cnt_cfg = PltCntCfg()
        pl_in = PlotInput(bench_cfg, rv, plt_cnt_cfg)
        result = cp.boxplot(pl_in)
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], pn.panel)
