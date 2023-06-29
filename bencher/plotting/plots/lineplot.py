from typing import Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import panel as pn
import seaborn as sns

from bencher.plotting.plot_filter import PlotFilter, PlotInput, VarRange
from bencher.plotting.plot_types import PlotTypes
from bencher.plotting.plots.catplot import Catplot


class Lineplot:
    # shared plot filter for catplots
    plot_filter = PlotFilter(
        float_range=VarRange(1, 1),
        cat_range=VarRange(0, None),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )

    def lineplot(self, pl_in: PlotInput) -> Optional[pn.panel]:
        if self.plot_filter.matches(pl_in.plt_cnt_cfg):
            df, sns_cfg = Catplot.plot_setup(pl_in)
            sns_cfg.kind = "line"
            fg = sns.relplot(df, **sns_cfg.as_sns_args())
            return Catplot.plot_postprocess(fg, sns_cfg, PlotTypes.lineplot)
        return None
