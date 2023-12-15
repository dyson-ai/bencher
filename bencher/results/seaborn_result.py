import matplotlib.pyplot as plt
import panel as pn
import seaborn as sns
import matplotlib

from bencher.variables.parametrised_sweep import ParametrizedSweep
from bencher.variables.results import ResultVar, ResultVec
from bencher.plotting.plt_cnt_cfg import PltCfgBase
from bencher.results.bench_result_base import BenchResultBase


class SeabornResult(BenchResultBase):
    def plot_sns(self, rv: ParametrizedSweep, sns_cfg: PltCfgBase) -> pn.pane:
        """Plot with seaborn

        Args:
            bench_cfg (BenchCfg): bench config
            rv (ParametrizedSweep): the result variable to plot
            sns_cfg (PltCfgBase): the plot configuration

        Returns:
            pn.pane: A seaborn plot as a panel pane
        """
        matplotlib.use("agg")

        # bench_res = wrap_long_time_labels(bench_res.bench_cfg)

        plt.rcParams.update({"figure.max_open_warning": 0})

        # if type(rv) == ResultVec:
        # return plot_scatter_sns(bench_cfg, rv)
        # else:

        if type(rv) == ResultVec:
            if rv.size == 2:
                plt.figure(figsize=(4, 4))
                fg = self.plot_scatter2D_sns(rv)
            else:
                return pn.pane.Markdown("Scatter plots of >3D result vectors not supported yet")
        elif type(rv) == ResultVar:
            # self.to_pandas()
            df = self.ds[rv.name].to_dataframe().reset_index()

            try:
                fg = sns_cfg.plot_callback(data=df, **sns_cfg.as_sns_args())
            except Exception as e:
                return pn.pane.Markdown(
                    f"Was not able to plot becuase of exception:{e} \n this is likely due to too many NAN values"
                )

            # TODO try to set this during the initial plot rather than after
            for ax in fg.axes.flatten():
                for tick in ax.get_xticklabels():
                    tick.set_rotation(45)

            fg.set_xlabels(label=sns_cfg.xlabel, clear_inner=True)
            fg.set_ylabels(label=sns_cfg.ylabel, clear_inner=True)
        else:
            return None

        fg.fig.suptitle(sns_cfg.title)
        plt.tight_layout()

        return pn.panel(plt.gcf())

    def plot_scatter2D_sns(self, rv: ParametrizedSweep) -> pn.pane.Plotly:
        """Given a benchCfg generate a 2D scatter plot from seaborn

        Args:
            bench_cfg (BenchCfg): description of benchmark
            rv (ParametrizedSweep): result variable to plot

        Returns:
            pn.pane.Plotly: A 3d volume plot as a holoview in a pane
        """

        # bench_cfg = wrap_long_time_labels(bench_cfg)
        ds = self.ds.drop_vars("repeat")

        df = ds.to_dataframe().reset_index()

        names = rv.index_names()

        if self.bench_cfg.input_vars:
            h = sns.jointplot(df, x=names[0], y=names[1], hue=self.bench_cfg.input_vars[0].name)
        elif self.bench_cfg.over_time:
            h = sns.jointplot(df, x=names[0], y=names[1], hue=self.bench_cfg.iv_time[0].name)

        else:
            h = sns.jointplot(df, x=names[0], y=names[1])

        h.set_axis_labels(f"{names[0]} [{rv.units}]", f"{names[1]} [{rv.units}]")
        return h
