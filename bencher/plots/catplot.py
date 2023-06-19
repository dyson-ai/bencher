from bencher.plot_signature import PlotProvider, PlotFilter, VarRange
from bencher.bench_cfg import BenchCfg
from bencher.bench_vars import ParametrizedSweep
from bencher.plt_cfg import PltCntCfg, PltCfgBase

# from bencher import BenchCfg, ResultVec, ResultVar, BenchPlotter, ParametrizedSweep
from typing import List
import seaborn as sns
import panel as pn
import matplotlib.pyplot as plt
from strenum import StrEnum
from enum import auto


# class CatPlotTypes(StrEnum):
#     swarmplot = auto()
#     barplot = auto()
#     violinplot = auto()
#     boxenplot = auto()


class Catplot(PlotProvider):
    no_float_1_cat = PlotFilter(
        float_range=VarRange(0, 0),
        cat_range=VarRange(0, None),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )

    # def __init__(self):
    #     pass
    #     # self.register_plot(self.swarmplot)
    #     # self.register_plot(self.boxplot)
    #     # self.register_plot(self.barplot)
    #     # self.register_plot(self.violinplot)
    #     # self.register_plot(self.boxenplot)

    def plot_setup(self, bench_cfg: BenchCfg, rv: ParametrizedSweep, plt_cnt_cfg: PltCntCfg):
        plt.figure(figsize=(4, 4))
        df = bench_cfg.ds[rv.name].to_dataframe().reset_index()
        sns_cfg = PltCfgBase()
        sns_cfg.x = bench_cfg.input_vars[0].name
        x_units = bench_cfg.input_vars[0].units
        sns_cfg.y = rv.name
        sns_cfg.xlabel = f"{sns_cfg.x} [{x_units}]"
        sns_cfg.ylabel = f"{sns_cfg.y} [{rv.units}]"
        sns_cfg.title = f"{sns_cfg.x} vs {sns_cfg.y}"
        return df, sns_cfg

    def plot_postprocess(self, fg, sns_cfg, name):
        fg.fig.suptitle(sns_cfg.title)
        fg.set_xlabels(label=sns_cfg.xlabel, clear_inner=True)
        fg.set_ylabels(label=sns_cfg.ylabel, clear_inner=True)
        plt.tight_layout()
        return [pn.panel(plt.gcf(), name=name)]

    def swarmplot(
        self, bench_cfg: BenchCfg, rv: ParametrizedSweep, plt_cnt_cfg: PltCntCfg
    ) -> List[pn.panel]:
        name = "swarm"
        if self.no_float_1_cat.matches(plt_cnt_cfg):
            df, sns_cfg = self.plot_setup(bench_cfg, rv, plt_cnt_cfg)
            sns_cfg.kind = name
            fg = sns.catplot(df, **sns_cfg.as_sns_args())
            return self.plot_postprocess(fg, sns_cfg, name)
        return []

    def boxplot(
        self, bench_cfg: BenchCfg, rv: ParametrizedSweep, plt_cnt_cfg: PltCntCfg
    ) -> List[pn.panel]:
        if self.no_float_1_cat.matches(plt_cnt_cfg):
            df, sns_cfg = self.plot_setup(bench_cfg, rv, plt_cnt_cfg)
            sns_cfg.kind = "box"
            fg = sns.catplot(df, x=sns_cfg.x, y=sns_cfg.y, kind=sns_cfg.kind)
            return self.plot_postprocess(fg, sns_cfg, sns_cfg.kind)
        return []

    def barplot(
        self, bench_cfg: BenchCfg, rv: ParametrizedSweep, plt_cnt_cfg: PltCntCfg
    ) -> List[pn.panel]:
        if self.no_float_1_cat.matches(plt_cnt_cfg):
            df, sns_cfg = self.plot_setup(bench_cfg, rv, plt_cnt_cfg)
            sns_cfg.kind = "bar"
            fg = sns.catplot(df, x=sns_cfg.x, y=sns_cfg.y, kind=sns_cfg.kind)
            return self.plot_postprocess(fg, sns_cfg, sns_cfg.kind)
        return []

    def boxenplot(
        self, bench_cfg: BenchCfg, rv: ParametrizedSweep, plt_cnt_cfg: PltCntCfg
    ) -> List[pn.panel]:
        if self.no_float_1_cat.matches(plt_cnt_cfg):
            df, sns_cfg = self.plot_setup(bench_cfg, rv, plt_cnt_cfg)
            sns_cfg.kind = "boxen"
            fg = sns.catplot(df, x=sns_cfg.x, y=sns_cfg.y, kind=sns_cfg.kind)
            return self.plot_postprocess(fg, sns_cfg, sns_cfg.kind)
        return []

    def violinplot(
        self, bench_cfg: BenchCfg, rv: ParametrizedSweep, plt_cnt_cfg: PltCntCfg
    ) -> List[pn.panel]:
        if self.no_float_1_cat.matches(plt_cnt_cfg):
            df, sns_cfg = self.plot_setup(bench_cfg, rv, plt_cnt_cfg)
            sns_cfg.kind = "violin"
            fg = sns.catplot(df, **sns_cfg.as_sns_args())
            return self.plot_postprocess(fg, sns_cfg, sns_cfg.kind)
        return []
