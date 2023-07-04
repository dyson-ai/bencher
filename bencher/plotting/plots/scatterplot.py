import matplotlib.pyplot as plt
import panel as pn
import seaborn as sns
from typing import Optional

from bencher.plotting.plot_filter import PlotFilter, PlotInput, VarRange
from bencher.plotting.plot_types import PlotTypes
from bencher.plotting_functions import wrap_long_time_labels


class Scatter:
    """A class to display the result data as a scatter plot"""

    def scatter2D_sns(self, pl_in: PlotInput) -> Optional[pn.panel]:
        """Given a benchCfg generate a 2D scatter plot from seaborn

        Args:
            pl_in (PlotInput): data to plot

        Returns:
            Optional[pn.pane]: A panel pane with a scatter plot
        """

        if PlotFilter(
            float_range=VarRange(None, None),
            cat_range=VarRange(None, None),
            vector_len=VarRange(2, 2),
        ).matches(pl_in.plt_cnt_cfg):
            bench_cfg = wrap_long_time_labels(pl_in.bench_cfg)
            ds = bench_cfg.ds.drop_vars("repeat")

            df = ds.to_dataframe().reset_index()

            names = pl_in.rv.index_names()

            if bench_cfg.input_vars:
                h = sns.jointplot(df, x=names[0], y=names[1], hue=bench_cfg.input_vars[0].name)
            elif bench_cfg.over_time:
                h = sns.jointplot(df, x=names[0], y=names[1], hue=bench_cfg.iv_time[0].name)

            else:
                h = sns.jointplot(df, x=names[0], y=names[1])

            h.set_axis_labels(f"{names[0]} [{pl_in.rv.units}]", f"{names[1]} [{pl_in.rv.units}]")
            plt.tight_layout()
            return pn.panel(h.fig, name=PlotTypes.scatter2D_sns)
        return None
