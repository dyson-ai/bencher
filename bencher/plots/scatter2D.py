from bencher.plotting_functions import (
    PlotProvider,
    PlotSignature,
    VarRange,
    PltCntCfg,
    PltCfgBase,
)
from bencher import BenchCfg, ResultVec, ResultVar, ParametrizedOutput
from typing import List
import panel as pn
import plotly.graph_objs as go
import plotly.express as px
import seaborn as sns


class Scatter2D(PlotProvider):
    def get_plot_signatures(self):
        plot_sig = PlotSignature()
        plot_sig.cat_range = VarRange(0, None)
        plot_sig.vector_len = VarRange(2, 2)
        return plot_sig

    def plot_single(self, plot_sig: PlotSignature, bench_cfg: BenchCfg, rv: ResultVec):
        self.plot_scatter2D_sns(bench_cfg, rv)

    def plot_scatter2D_sns(
        self, bench_cfg: BenchCfg, rv: ParametrizedOutput
    ) -> pn.pane.Plotly:
        """Given a benchCfg generate a 2D scatter plot from seaborn

        Args:
            bench_cfg (BenchCfg): description of benchmark
            rv (ParametrizedOutput): result variable to plot

        Returns:
            pn.pane.Plotly: A 3d volume plot as a holoview in a pane
        """

        bench_cfg = self.wrap_long_time_labels(bench_cfg)
        ds = bench_cfg.ds.drop_vars("repeat")

        df = ds.to_dataframe().reset_index()

        names = rv.index_names()

        if bench_cfg.input_vars:
            h = sns.jointplot(
                df, x=names[0], y=names[1], hue=bench_cfg.input_vars[0].name
            )
        elif bench_cfg.over_time:
            h = sns.jointplot(df, x=names[0], y=names[1], hue=bench_cfg.iv_time[0].name)

        else:
            h = sns.jointplot(df, x=names[0], y=names[1])

        h.set_axis_labels(f"{names[0]} [{rv.units}]", f"{names[1]} [{rv.units}]")
        return h

    def plot_scatter2D_hv(
        self, bench_cfg: BenchCfg, rv: ParametrizedOutput
    ) -> pn.pane.Plotly:
        """Given a benchCfg generate a 2D scatter plot

        Args:
            bench_cfg (BenchCfg): description of benchmark
            rv (ParametrizedOutput): result variable to plot

        Returns:
            pn.pane.Plotly: A 3d volume plot as a holoview in a pane
        """

        bench_cfg = self.wrap_long_time_labels(bench_cfg)
        ds = bench_cfg.ds.drop_vars("repeat")

        df = bench_cfg.ds.to_dataframe().reset_index()

        names = rv.index_names()

        return px.scatter(
            df, x=names[0], y=names[1], marginal_x="histogram", marginal_y="histogram"
        )
