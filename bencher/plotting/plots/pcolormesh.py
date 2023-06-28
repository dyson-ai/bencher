from typing import List, Tuple
import seaborn as sns
import panel as pn
import matplotlib.pyplot as plt
import pandas as pd
from bencher.plotting.plot_filter import PlotFilter, VarRange, PlotInput
from bencher.plt_cfg import PltCfgBase
from bencher.plotting.plot_types import PlotTypes

import plotly.graph_objects as go


class PColormesh:
    # shared plot filter for catplots
    plot_filter = PlotFilter(
        float_range=VarRange(2, 2),
        cat_range=VarRange(0, 0),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )

    # @staticmethod
    # def plot_setup(pl_in: PlotInput) -> Tuple[pd.DataFrame, PltCfgBase]:
    #     plt.figure(figsize=(4, 4))
    #     df = pl_in.bench_cfg.ds[pl_in.rv.name].to_dataframe().reset_index()
    #     sns_cfg = PltCfgBase()
    #     sns_cfg.x = pl_in.bench_cfg.input_vars[0].name
    #     x_units = pl_in.bench_cfg.input_vars[0].units
    #     sns_cfg.y = pl_in.rv.name
    #     sns_cfg.xlabel = f"{sns_cfg.x} [{x_units}]"
    #     sns_cfg.ylabel = f"{sns_cfg.y} [{pl_in.rv.units}]"
    #     sns_cfg.title = f"{sns_cfg.x} vs {sns_cfg.y}"
    #     return df, sns_cfg

    def pcolormesh(self, pl_in: PlotInput) -> List[pn.panel]:
        if self.plot_filter.matches(pl_in.plt_cnt_cfg):
            # print("I match")
            # print(pl_in.bench_cfg.ds[pl_in.rv.name])

            da = pl_in.bench_cfg.ds[pl_in.rv.name]
            mean = da.mean("repeat")

            # go.Contour()

            # return
            # return [pn.panel("lol", name=PlotTypes.pcolormesh)]
            return [pn.panel(mean.plot(), name=PlotTypes.pcolormesh)]

        print("I DONT MATCH")
        return []

    # @staticmethod
    # def plot_postprocess(fg: plt.figure, sns_cfg: PltCfgBase, name: str) -> List[pn.panel]:
    #     fg.fig.suptitle(sns_cfg.title)
    #     fg.set_xlabels(label=sns_cfg.xlabel, clear_inner=True)
    #     fg.set_ylabels(label=sns_cfg.ylabel, clear_inner=True)
    #     plt.tight_layout()
    #     return [pn.panel(fg.fig, name=name)]

    # def catplot_common(self, pl_in: PlotInput, kind: str, name: str) -> List[pn.panel]:
    #     if self.filter.matches(pl_in.plt_cnt_cfg):
    #         df, sns_cfg = self.plot_setup(pl_in)
    #         sns_cfg.kind = kind
    #         fg = sns.catplot(df, **sns_cfg.as_sns_args())
    #         return self.plot_postprocess(fg, sns_cfg, name)
    #     return []

    # def swarmplot(self, pl_in: PlotInput) -> List[pn.panel]:
    #     return self.catplot_common(pl_in, "swarm", PlotTypes.swarmplot)

    # def violinplot(self, pl_in: PlotInput) -> List[pn.panel]:
    #     return self.catplot_common(pl_in, "violin", PlotTypes.violinplot)

    # def boxplot(self, pl_in: PlotInput) -> List[pn.panel]:
    #     return self.catplot_common(pl_in, "box", PlotTypes.boxplot)

    # def barplot(self, pl_in: PlotInput) -> List[pn.panel]:
    #     return self.catplot_common(pl_in, "bar", PlotTypes.barplot)

    # def boxenplot(self, pl_in: PlotInput) -> List[pn.panel]:
    #     return self.catplot_common(pl_in, "boxen", PlotTypes.boxenplot)
