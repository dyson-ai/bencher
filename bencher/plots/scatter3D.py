
from bencher.plotting_functions import PlotProvider, PlotSignature,VarRange
from bencher import BenchCfg,ResultVec
from typing import List
import panel as pn

class Scatter3D(PlotProvider):
    def get_plot_signatures(self):
        plot_sig = PlotSignature()
        plot_sig.cat_range = VarRange(0, None)
        plot_sig.vector_len = VarRange(3, 3)
        return plot_sig

    def plot_single(
        self, plot_sig: PlotSignature, bench_cfg: BenchCfg, result_vars: List[ResultVec]
    ):
        """Given a benchCfg generate a 3D scatter plot with plotly express

        Args:
            bench_cfg (BenchCfg): description of benchmark
            rv (ParametrizedOutput): result variable to plot

        Returns:
            pn.pane.Plotly: A 3d scatter plot as a holoview in a pane
        """
        bench_cfg = wrap_long_time_labels(bench_cfg)

        df = bench_cfg.ds.to_dataframe().reset_index()

        names = rv.index_names()  # get the column names of the vector result

        if bench_cfg.input_vars:
            color = bench_cfg.input_vars[0].name
        else:
            color = None

        if bench_cfg.over_time:
            if len(names) < 3:  # only a 2d vector result so use the time axis as the third point
                names.insert(0, bench_cfg.iv_time[0].name)

        return px.scatter_3d(
            df, x=names[0], y=names[1], z=names[2], color=color, symbol=color, size_max=2
        )

    def plot_scatter3D_px(bench_cfg: BenchCfg, rv: ParametrizedOutput) -> pn.pane.Plotly:
        """Given a benchCfg generate a 3D scatter plot with plotly express

        Args:
            bench_cfg (BenchCfg): description of benchmark
            rv (ParametrizedOutput): result variable to plot

        Returns:
            pn.pane.Plotly: A 3d scatter plot as a holoview in a pane
        """

        bench_cfg = wrap_long_time_labels(bench_cfg)

        df = bench_cfg.ds.to_dataframe().reset_index()

        names = rv.index_names()  # get the column names of the vector result

        if bench_cfg.input_vars:
            color = bench_cfg.input_vars[0].name
        else:
            color = None

        if bench_cfg.over_time:
            if len(names) < 3:  # only a 2d vector result so use the time axis as the third point
                names.insert(0, bench_cfg.iv_time[0].name)

        return px.scatter_3d(
            df, x=names[0], y=names[1], z=names[2], color=color, symbol=color, size_max=2
        )