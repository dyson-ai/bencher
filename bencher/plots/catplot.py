from bencher.plot_signature import PlotFilter, VarRange, PlotInput
from bencher.plt_cfg import PltCntCfg, PltCfgBase

from typing import List
import seaborn as sns
import panel as pn
import matplotlib.pyplot as plt


class Catplot:
    # shared plot filter for catplots
    float_1_cat_any_vec_1_res_1_ = PlotFilter(
        float_range=VarRange(0, 0),
        cat_range=VarRange(0, None),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )

    def plot_setup(self, pl_in: PlotInput):
        plt.figure(figsize=(4, 4))
        df = pl_in.bench_cfg.ds[pl_in.rv.name].to_dataframe().reset_index()
        sns_cfg = PltCfgBase()
        sns_cfg.x = pl_in.bench_cfg.input_vars[0].name
        x_units = pl_in.bench_cfg.input_vars[0].units
        sns_cfg.y = pl_in.rv.name
        sns_cfg.xlabel = f"{sns_cfg.x} [{x_units}]"
        sns_cfg.ylabel = f"{sns_cfg.y} [{pl_in.rv.units}]"
        sns_cfg.title = f"{sns_cfg.x} vs {sns_cfg.y}"
        return df, sns_cfg

    def plot_postprocess(self, fg, sns_cfg, name):
        fg.fig.suptitle(sns_cfg.title)
        fg.set_xlabels(label=sns_cfg.xlabel, clear_inner=True)
        fg.set_ylabels(label=sns_cfg.ylabel, clear_inner=True)
        plt.tight_layout()
        return [pn.panel(plt.gcf(), name=name)]

    # def catplot_common(self, pl_in: PlotInput,kind) -> List[pn.panel]:

    def swarmplot(self, pl_in: PlotInput) -> List[pn.panel]:
        name = "swarm"
        if self.float_1_cat_any_vec_1_res_1_.matches(pl_in.plt_cnt_cfg):
            df, sns_cfg = self.plot_setup(pl_in)
            sns_cfg.kind = name
            fg = sns.catplot(df, **sns_cfg.as_sns_args())
            return self.plot_postprocess(fg, sns_cfg, name)
        return []

    def boxplot(self, pl_in: PlotInput) -> List[pn.panel]:
        if self.float_1_cat_any_vec_1_res_1_.matches(pl_in.plt_cnt_cfg):
            df, sns_cfg = self.plot_setup(pl_in)
            sns_cfg.kind = "box"
            fg = sns.catplot(df, x=sns_cfg.x, y=sns_cfg.y, kind=sns_cfg.kind)
            return self.plot_postprocess(fg, sns_cfg, sns_cfg.kind)
        return []

    def barplot(self, pl_in: PlotInput) -> List[pn.panel]:
        if self.float_1_cat_any_vec_1_res_1_.matches(pl_in.plt_cnt_cfg):
            df, sns_cfg = self.plot_setup(pl_in)
            sns_cfg.kind = "bar"
            fg = sns.catplot(df, x=sns_cfg.x, y=sns_cfg.y, kind=sns_cfg.kind)
            return self.plot_postprocess(fg, sns_cfg, sns_cfg.kind)
        return []

    def boxenplot(self, pl_in: PlotInput) -> List[pn.panel]:
        if self.float_1_cat_any_vec_1_res_1_.matches(pl_in.plt_cnt_cfg):
            df, sns_cfg = self.plot_setup(pl_in)
            sns_cfg.kind = "boxen"
            fg = sns.catplot(df, x=sns_cfg.x, y=sns_cfg.y, kind=sns_cfg.kind)
            return self.plot_postprocess(fg, sns_cfg, sns_cfg.kind)
        return []

    def violinplot(self, pl_in: PlotInput) -> List[pn.panel]:
        if self.float_1_cat_any_vec_1_res_1_.matches(pl_in.plt_cnt_cfg):
            df, sns_cfg = self.plot_setup(pl_in)
            sns_cfg.kind = "violin"
            fg = sns.catplot(df, **sns_cfg.as_sns_args())
            return self.plot_postprocess(fg, sns_cfg, sns_cfg.kind)
        return []
