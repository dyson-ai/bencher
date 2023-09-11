from textwrap import wrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import panel as pn
import plotly.express as px
import seaborn as sns

from bencher.bench_cfg import BenchCfg, PltCfgBase
from bencher.variables.parametrised_sweep import ParametrizedSweep

from bencher.variables.results import ResultVar, ResultVec
import matplotlib


# hv.extension("plotly", "bokeh")
# hv.extension("plotly")


def wrap_long_time_labels(bench_cfg: BenchCfg) -> BenchCfg:
    """Takes a benchCfg and wraps any index labels that are too long to be plotted easily

    Args:
        bench_cfg (BenchCfg):

    Returns:
        BenchCfg: updated config with wrapped labels
    """
    if bench_cfg.over_time:
        if bench_cfg.ds.coords["over_time"].dtype == np.datetime64:
            # plotly catastrophically fails to plot anything with the default long string representation of time, so convert to a shorter time representation
            bench_cfg.ds.coords["over_time"] = [
                pd.to_datetime(t).strftime("%d-%m-%y %H-%M-%S")
                for t in bench_cfg.ds.coords.coords["over_time"].values
            ]
            # wrap very long time event labels because otherwise the graphs are unreadable
        if bench_cfg.time_event is not None:
            bench_cfg.ds.coords["over_time"] = [
                "\n".join(wrap(t, 20)) for t in bench_cfg.ds.coords["over_time"].values
            ]
    return bench_cfg


def plot_sns(bench_cfg: BenchCfg, rv: ParametrizedSweep, sns_cfg: PltCfgBase) -> pn.pane:
    """Plot with seaborn

    Args:
        bench_cfg (BenchCfg): bench config
        rv (ParametrizedSweep): the result variable to plot
        sns_cfg (PltCfgBase): the plot configuration

    Returns:
        pn.pane: A seaborn plot as a panel pane
    """
    matplotlib.use("agg")

    bench_cfg = wrap_long_time_labels(bench_cfg)

    plt.rcParams.update({"figure.max_open_warning": 0})

    # if type(rv) == ResultVec:
    # return plot_scatter_sns(bench_cfg, rv)
    # else:

    if type(rv) == ResultVec:
        if rv.size == 2:
            plt.figure(figsize=(4, 4))
            fg = plot_scatter2D_sns(bench_cfg, rv)
        else:
            return pn.pane.Markdown("Scatter plots of >3D result vectors not supported yet")
    elif type(rv) == ResultVar:
        df = bench_cfg.ds[rv.name].to_dataframe().reset_index()

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

    fg.fig.suptitle(sns_cfg.title)
    plt.tight_layout()

    return pn.panel(plt.gcf())


def plot_scatter2D_sns(bench_cfg: BenchCfg, rv: ParametrizedSweep) -> pn.pane.Plotly:
    """Given a benchCfg generate a 2D scatter plot from seaborn

    Args:
        bench_cfg (BenchCfg): description of benchmark
        rv (ParametrizedSweep): result variable to plot

    Returns:
        pn.pane.Plotly: A 3d volume plot as a holoview in a pane
    """

    bench_cfg = wrap_long_time_labels(bench_cfg)
    ds = bench_cfg.ds.drop_vars("repeat")

    df = ds.to_dataframe().reset_index()

    names = rv.index_names()

    if bench_cfg.input_vars:
        h = sns.jointplot(df, x=names[0], y=names[1], hue=bench_cfg.input_vars[0].name)
    elif bench_cfg.over_time:
        h = sns.jointplot(df, x=names[0], y=names[1], hue=bench_cfg.iv_time[0].name)

    else:
        h = sns.jointplot(df, x=names[0], y=names[1])

    h.set_axis_labels(f"{names[0]} [{rv.units}]", f"{names[1]} [{rv.units}]")
    return h


def plot_scatter2D_hv(bench_cfg: BenchCfg, rv: ParametrizedSweep) -> pn.pane.Plotly:
    """Given a benchCfg generate a 2D scatter plot

    Args:
        bench_cfg (BenchCfg): description of benchmark
        rv (ParametrizedSweep): result variable to plot

    Returns:
        pn.pane.Plotly: A 3d volume plot as a holoview in a pane
    """

    bench_cfg = wrap_long_time_labels(bench_cfg)
    bench_cfg.ds.drop_vars("repeat")

    df = bench_cfg.get_dataframe()

    names = rv.index_names()

    return px.scatter(df, x=names[0], y=names[1], marginal_x="histogram", marginal_y="histogram")
