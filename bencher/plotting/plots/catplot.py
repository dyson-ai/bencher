from typing import Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import panel as pn
import seaborn as sns

from bencher.plotting.plot_filter import PlotFilter, PlotInput, VarRange
from bencher.plotting.plot_types import PlotTypes
from bencher.plt_cfg import PltCfgBase


class Catplot:
    # shared plot filter for catplots
    float_0_cat_at_least1_vec_1_res_1 = PlotFilter(
        float_range=VarRange(0, 0),
        cat_range=VarRange(1, None),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )

    @staticmethod
    def plot_setup(pl_in: PlotInput) -> Tuple[pd.DataFrame, PltCfgBase]:
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

    @staticmethod
    def plot_postprocess(fg: plt.figure, sns_cfg: PltCfgBase, name: str) -> Optional[pn.panel]:
        fg.fig.suptitle(sns_cfg.title)
        fg.set_xlabels(label=sns_cfg.xlabel, clear_inner=True)
        fg.set_ylabels(label=sns_cfg.ylabel, clear_inner=True)
        plt.tight_layout()
        return pn.panel(fg.fig, name=name)

    def catplot_common(self, pl_in: PlotInput, kind: str, name: str) -> Optional[pn.panel]:
        if self.float_0_cat_at_least1_vec_1_res_1.matches(pl_in.plt_cnt_cfg):
            df, sns_cfg = self.plot_setup(pl_in)
            sns_cfg.kind = kind
            fg = sns.catplot(df, **sns_cfg.as_sns_args())
            return self.plot_postprocess(fg, sns_cfg, name)
        return None

    def swarmplot(self, pl_in: PlotInput) -> Optional[pn.panel]:
        return self.catplot_common(pl_in, "swarm", PlotTypes.swarmplot)

    def violinplot(self, pl_in: PlotInput) -> Optional[pn.panel]:
        return self.catplot_common(pl_in, "violin", PlotTypes.violinplot)

    def boxplot(self, pl_in: PlotInput) -> Optional[pn.panel]:
        return self.catplot_common(pl_in, "box", PlotTypes.boxplot)

    def barplot(self, pl_in: PlotInput) -> Optional[pn.panel]:
        return self.catplot_common(pl_in, "bar", PlotTypes.barplot)

    def boxenplot(self, pl_in: PlotInput) -> Optional[pn.panel]:
        return self.catplot_common(pl_in, "boxen", PlotTypes.boxenplot)
