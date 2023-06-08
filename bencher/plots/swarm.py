from bencher.plotting_functions import PlotProvider, PlotSignature,VarRange,PltCntCfg,PltCfgBase
from bencher import BenchCfg,ResultVec,ResultVar,ParametrizedOutput
from typing import List
import panel as pn
import plotly.graph_objs as go
import matplotlib.pyplot as plt


class PlotSwarm(PlotProvider):
    def get_plot_signatures(self):
        plot_sig = PlotSignature()
        plot_sig.float_cnt = VarRange(2, 2)
        plot_sig.cat_range = VarRange(0, 0)
        plot_sig.vector_len = VarRange(0, 0)
        return plot_sig

    def plot_sns(self,bench_cfg: BenchCfg, rv: ParametrizedOutput, sns_cfg: PltCfgBase) -> pn.pane:
        """Plot with seaborn

        Args:
            bench_cfg (BenchCfg): bench config
            rv (ParametrizedOutput): the result variable to plot
            sns_cfg (PltCfgBase): the plot configuration

        Returns:
            pn.pane: A seaborn plot as a panel pane
        """

        bench_cfg = self.wrap_long_time_labels(bench_cfg)

        plt.rcParams.update({"figure.max_open_warning": 0})

        # if type(rv) == ResultVec:
        # return plot_scatter_sns(bench_cfg, rv)
        # else:

        # if type(rv) == ResultVec:
        #     if rv.size == 2:
        #         plt.figure(figsize=(4, 4))
        #         fg = plot_scatter2D_sns(bench_cfg, rv)
        #     elif rv.size == 3:
        #         return plot_scatter3D_px(bench_cfg, rv)
        #     else:
        #         return pn.pane.Markdown("Scatter plots of >3D result vectors not supported yet")
        # else:
        df = bench_cfg.ds[rv.name].to_dataframe().reset_index()

        fg = sns_cfg.plot_callback(data=df, **sns_cfg.as_sns_args())

        # TODO try to set this during the initial plot rather than after
        if bench_cfg.over_time:
            for ax in fg.axes.flatten():
                for tick in ax.get_xticklabels():
                    tick.set_rotation(45)

        fg.set_xlabels(label=sns_cfg.xlabel, clear_inner=True)
        fg.set_ylabels(label=sns_cfg.ylabel, clear_inner=True)
        fg.fig.suptitle(sns_cfg.title)
        plt.tight_layout()

        if bench_cfg.save_fig:
            self.save_fig(bench_cfg, sns_cfg)
        return pn.panel(plt.gcf(), sizing_mode="scale_height")
