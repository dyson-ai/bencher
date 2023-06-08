import os
import errno
import matplotlib.pyplot as plt
import panel as pn
import numpy as np
import plotly.graph_objs as go
import holoviews as hv
import pandas as pd
import seaborn as sns
import plotly.express as px

import logging

from holoviews import opts
from bencher.bench_vars import ParametrizedOutput, ResultVec
from bencher.bench_cfg import PltCfgBase, BenchCfg
from bencher.plotting_functions import PlotSignature

hv.extension("plotly")

from textwrap import wrap

from abc import ABC
from typing import List
import param


class VarRange:

    # lower_bound = param.Integer(0)
    # upper_bound = param.Integer(0)

    def __init__(self, lower_bound=0, upper_bound=0) -> None:
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        # self.float_range = VarRange()
        # self.cat_range = VarRange()


class PlotSignature:

    float_cnt = param.Integer(0, doc="The number of float variables to plot")
    cat_cnt = param.Integer(0, doc="The number of cat variables")
    vector_len = param.Integer(0, doc="The number of cat variables")

    def __init__(self) -> None:
        self.float_range = VarRange(0, 0)
        self.cat_range = VarRange(0, 0)
        self.vector_len = VarRange(1, 1)
        self.result_vars = VarRange(1, 1)


class PlotProvider(ABC):
    def __init__(self) -> None:
        pass

    def get_plot_signatures(self):
        # must implement
        pass

    def plot_single(plot_sig: PlotSignature, bench_cfg: BenchCfg, rv: ResultVec):
        pass

    def plot_multi(plot_sig: PlotSignature, bench_cfg: BenchCfg, result_vars: List[ResultVec]):
        pass









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


def plot_sns(bench_cfg: BenchCfg, rv: ParametrizedOutput, sns_cfg: PltCfgBase) -> pn.pane:
    """Plot with seaborn

    Args:
        bench_cfg (BenchCfg): bench config
        rv (ParametrizedOutput): the result variable to plot
        sns_cfg (PltCfgBase): the plot configuration

    Returns:
        pn.pane: A seaborn plot as a panel pane
    """

    bench_cfg = wrap_long_time_labels(bench_cfg)

    if bench_cfg.use_holoview:
        opts.defaults(
            opts.Curve(
                colorbar=True,
                colorbar_opts={"title": rv.name},
                width=600,
                height=600,
                xlabel=sns_cfg.xlabel,
                ylabel=sns_cfg.ylabel,
                title=sns_cfg.title,
            )
        )
        ds = hv.Dataset(bench_cfg.ds[rv.name].mean("repeat"))

        if bench_cfg.over_time:
            agg = ds.aggregate("over_time", np.mean, spreadfn=np.std)
            plot = hv.Spread(agg) * hv.Curve(agg)
        else:
            plot = ds.to(hv.Bars) * ds.to(hv.Scatter).opts(jitter=50)
        return plot
    else:
        plt.rcParams.update({"figure.max_open_warning": 0})

        # if type(rv) == ResultVec:
        # return plot_scatter_sns(bench_cfg, rv)
        # else:

        if type(rv) == ResultVec:
            if rv.size == 2:
                plt.figure(figsize=(4, 4))
                fg = plot_scatter2D_sns(bench_cfg, rv)
            elif rv.size == 3:
                return plot_scatter3D_px(bench_cfg, rv)
            else:
                return pn.pane.Markdown("Scatter plots of >3D result vectors not supported yet")
        else:
            df = bench_cfg.ds[rv.name].to_dataframe().reset_index()

            try:
                fg = sns_cfg.plot_callback(data=df, **sns_cfg.as_sns_args())
            except Exception as e:
                return pn.pane.Markdown(
                    f"Was not able to plot becuase of exception:{e} \n this is likely due to too many NAN values"
                )

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
            save_fig(bench_cfg, sns_cfg)
        return pn.panel(plt.gcf())


def save_fig(
    bench_cfg: BenchCfg,
    sns_cfg: PltCfgBase,
):
    """Save a seaborn figure to disk based on bench config data

    Args:
        bench_cfg (BenchCfg): benchmark config
        sns_cfg (PltCfgBase): plotting config
    """
    sns_cfg.data = None  # remove data before getting __repr__ for filename
    figname = f"{bench_cfg.as_filename()},{sns_cfg.as_filename()}"
    figpath = os.path.join("autofig", bench_cfg.bench_name, f"{figname}.png")
    logging.info(f"saving:{figpath}")
    dir_name = os.path.dirname(figpath)
    if not os.path.exists(dir_name) and dir_name != "":
        try:
            os.makedirs(dir_name)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    if os.path.exists(figpath) and bench_cfg.raise_duplicate_exception:
        raise FileExistsError(
            f"This figname {figname} already exists, please define a unique benchmark name or don't run the same benchmark twice"
        )
    plt.savefig(figpath)

