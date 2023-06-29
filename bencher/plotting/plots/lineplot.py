from typing import Optional

import panel as pn
import seaborn as sns

from bencher.plotting.plot_filter import PlotFilter, PlotInput, VarRange
from bencher.plotting.plot_types import PlotTypes
from bencher.plotting.plots.catplot import Catplot
from bencher.plt_cfg import PltCfgBase


class Lineplot:
    # shared plot filter for catplots
    plot_filter = PlotFilter(
        float_range=VarRange(1, 1),
        cat_range=VarRange(0, 1),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )

    def lineplot(self, pl_in: PlotInput) -> Optional[pn.panel]:
        if self.plot_filter.matches(pl_in.plt_cnt_cfg):
            df, sns_cfg = Catplot.plot_setup(pl_in)
            sns_cfg = PltCfgBase()

            x = pl_in.plt_cnt_cfg.float_vars[0]
            y = pl_in.rv
            if pl_in.plt_cnt_cfg.cat_cnt > 0:
                sns_cfg.hue = pl_in.plt_cnt_cfg.cat_vars[0].name

            sns_cfg.x = x.name
            sns_cfg.y = y.name

            sns_cfg.kind = "line"
            sns_cfg.xlabel = f"{x.name} [{x.units}]"
            sns_cfg.ylabel = f"{sns_cfg.y} [{pl_in.rv.units}]"
            sns_cfg.title = f"{sns_cfg.x} vs {sns_cfg.y}"

            fg = sns.relplot(df, **sns_cfg.as_sns_args())

            return Catplot.plot_postprocess(fg, sns_cfg, PlotTypes.lineplot)
        return None
