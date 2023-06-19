from bencher.plot_signature import PlotProvider, PlotFilter, VarRange
from bencher.bench_cfg import BenchCfg
from bencher.bench_vars import ParametrizedSweep
from bencher.plt_cfg import PltCntCfg, PltCfgBase

# from bencher import BenchCfg, ResultVec, ResultVar, BenchPlotter, ParametrizedSweep
from typing import List
import seaborn as sns
import panel as pn
import matplotlib.pyplot as plt


class Tables(PlotProvider):
    no_float_1_cat = PlotFilter(
        float_range=VarRange(0, 0),
        cat_range=VarRange(0, None),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )

    def __init__(self):
        self.register_plot(self.dataframe_multi_index)
        self.register_plot(self.xarray)

    def dataframe_multi_index(
        self, bench_cfg: BenchCfg, rv: ParametrizedSweep, plt_cnt_cfg: PltCntCfg
    ) -> List[pn.panel]:
        name = "dataframe_multi_index"
        if self.no_float_1_cat.matches(plt_cnt_cfg):
            df = bench_cfg.get_dataframe()
            return [pn.pane.DataFrame(df, name=name)]
        return []

    def xarray(
        self, bench_cfg: BenchCfg, rv: ParametrizedSweep, plt_cnt_cfg: PltCntCfg
    ) -> List[pn.panel]:
        name = "xarray"
        if self.no_float_1_cat.matches(plt_cnt_cfg):
            return [pn.panel(bench_cfg.ds, name=name)]
        return []
