from typing import Optional

import panel as pn
import seaborn as sns
import seaborn.objects as so
import hvplot.pandas
import plotly.express as px
import plotly.graph_objects as go
import holoviews as hv
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show

from bencher.plotting.plot_filter import PlotFilter, PlotInput, VarRange
from bencher.plotting.plot_types import PlotTypes
from bencher.plotting.plots.catplot import Catplot
from bencher.plt_cfg import PltCfgBase


class Lineplot:
    # shared plot filter for lineplots
    plot_filter = PlotFilter(
        float_range=VarRange(1, 1),
        cat_range=VarRange(0, 1),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )

    def lineplot(self, pl_in: PlotInput) -> Optional[pn.panel]:
        """generate a line plot

        Args:
            pl_in (PlotInput): data to plot

        Returns:
            Optional[pn.panel]: a line plot of the data
        """
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

    def stacked_area_plot(self, pl_in: PlotInput) -> Optional[pn.panel]:
        """generate a stacked area plot

        Args:
            pl_in (PlotInput): data to plot

        Returns:
            Optional[pn.panel]: a stacked area plot of the data
        """
        if self.plot_filter.matches(pl_in.plt_cnt_cfg):
            x = pl_in.plt_cnt_cfg.float_vars[0]
            y = pl_in.rv
            hue = pl_in.plt_cnt_cfg.cat_vars[0]
            # df = pl_in.bench_cfg.get_dataframe()
            da = pl_in.bench_cfg.ds[y.name]

            mean = da.mean("repeat")
            df = mean.to_dataframe().reset_index()
            
            title = f"{x.name} vs {y.name}"
            xlabel = f"{x.name} [{x.units}]"
            ylabel = f"{y.name} [{y.units}]"

            print(df)


            # df_plot = df.hvplot.area(x = x.name, y = hue.values(debug=False), label = title)
            # df_plot = px.area(df, x = x.name, y = y.name, color=hue.name) 
            # df_plot = hv.Area(df, kdims=[x.name], vdims=[y.name]).groupby(hue.name).opts(stacked=True)
            # df_plot = hv.Area(df, kdims=[x.name], vdims=[y.name])
            # df_plot = so.Plot(df, x.name, y.name, color=hue.name).add(so.Area(alpha=.7), so.Stack())
            # p = figure()
            # df_plot = p.varea_stack(stackers=hue.values(debug = False), x= x.name, source=df)
            # df_plot = df.plot.area(x = x.name, y = y.name)
            # df_plot = plt.stackplot(x.name, y.name, labels=hue.values(debug=False))

            

            # return pn.panel(df_plot, name = PlotTypes.stacked_area_plot)
            # return pn.panel(p, name = PlotTypes.stacked_area_plot)
            return pn.panel(plt.gcf(), name = PlotTypes.stacked_area_plot)
        return None