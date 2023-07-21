import errno
import logging
import os
from textwrap import wrap

import holoviews as hv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import panel as pn
import plotly.express as px
import seaborn as sns
from holoviews import opts

from bencher.bench_cfg import BenchCfg, PltCfgBase
from bencher.bench_vars import ParametrizedSweep, ResultList, ResultVar, ResultVec
import plotly.graph_objs as go


hv.extension("plotly")


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
    elif type(rv) == ResultList:
        plt.figure(figsize=(4, 4))

        in_var = bench_cfg.input_vars[0].name

        # get the data to plot
        dataset_key = (bench_cfg.hash_value, rv.name)
        df = bench_cfg.ds_dynamic[dataset_key].to_dataframe().reset_index()

        # plot
        fg = sns.lineplot(df, x=rv.dim_name, y=rv.name, hue=in_var)

        # titles and labels and formatting
        fg.set_xlabel(f"{rv.dim_name} [{rv.dim_units}]")
        fg.set_ylabel(f"{rv.name} [{rv.units}]")
        fg.set_title(f"{in_var} vs ({rv.name} vs {rv.dim_name})")

        plt.tight_layout()

        return pn.panel(plt.gcf())

    fg.fig.suptitle(sns_cfg.title)
    plt.tight_layout()

    if bench_cfg.save_fig:
        save_fig(bench_cfg, sns_cfg)
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


def plot_scatter3D_px(bench_cfg: BenchCfg, rv: ParametrizedSweep) -> pn.pane.Plotly:
    """Given a benchCfg generate a 3D scatter plot with plotly express

    Args:
        bench_cfg (BenchCfg): description of benchmark
        rv (ParametrizedSweep): result variable to plot

    Returns:
        pn.pane.Plotly: A 3d scatter plot as a holoview in a pane
    """

    bench_cfg = wrap_long_time_labels(bench_cfg)

    df = bench_cfg.get_dataframe()

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


def plot_surface_plotly(
    bench_cfg: BenchCfg, rv: ParametrizedSweep, xr_cfg: PltCfgBase
) -> pn.pane.Plotly:
    """Given a benchCfg generate a 2D surface plot
    Args:
        bench_cfg (BenchCfg): description of benchmark
        rv (ParametrizedSweep): result variable to plot
        xr_cfg (PltCfgBase): config of x,y variables
    Returns:
        pn.pane.Plotly: A 2d surface plot as a holoview in a pane
    """

    if type(rv) == ResultVec:
        return plot_scatter3D_px(bench_cfg, rv)

    bench_cfg = wrap_long_time_labels(bench_cfg)

    da = bench_cfg.ds[rv.name].transpose()

    mean = da.mean("repeat")

    x = da.coords[xr_cfg.x]
    y = da.coords[xr_cfg.y]

    opacity = 0.3

    surfaces = [go.Surface(x=x, y=y, z=mean)]

    if bench_cfg.repeats > 1:
        std_dev = da.std("repeat")
        surfaces.append(go.Surface(x=x, y=y, z=mean + std_dev, showscale=False, opacity=opacity))
        surfaces.append(go.Surface(x=x, y=y, z=mean - std_dev, showscale=False, opacity=opacity))

    eye_dis = 1.7
    layout = go.Layout(
        title=xr_cfg.title,
        width=700,
        height=700,
        scene=dict(
            xaxis_title=xr_cfg.xlabel,
            yaxis_title=xr_cfg.ylabel,
            zaxis_title=xr_cfg.zlabel,
            camera={"eye": {"x": eye_dis, "y": eye_dis, "z": eye_dis}},
        ),
    )

    fig = {"data": surfaces, "layout": layout}

    return pn.pane.Plotly(fig)


def plot_surface_holo(
    bench_cfg: BenchCfg, rv: ParametrizedSweep, xr_cfg: PltCfgBase
) -> pn.pane.Plotly:
    """Given a benchCfg generate a 2D surface plot
    Args:
        bench_cfg (BenchCfg): description of benchmark
        rv (ParametrizedSweep): result variable to plot
        xr_cfg (PltCfgBase): config of x,y variables
    Returns:
        pn.pane.holoview: A 2d surface plot as a holoview in a pane
    """

    hv.extension("plotly")

    bench_cfg = wrap_long_time_labels(bench_cfg)

    alpha = 0.3

    da = bench_cfg.ds[rv.name]

    mean = da.mean("repeat")

    opts.defaults(
        opts.Surface(
            colorbar=True,
            width=800,
            height=800,
            zlabel=xr_cfg.zlabel,
            title=xr_cfg.title,
            # image_rtol=0.002,
        )
    )
    # TODO a warning suggests setting this parameter, but it does not seem to help as expected, leaving here to fix in the future
    # hv.config.image_rtol = 1.0

    ds = hv.Dataset(mean)
    surface = ds.to(hv.Surface)

    if bench_cfg.repeats > 1:
        std_dev = da.std("repeat")
        upper = hv.Dataset(mean + std_dev).to(hv.Surface).opts(alpha=alpha, colorbar=False)
        lower = hv.Dataset(mean - std_dev).to(hv.Surface).opts(alpha=alpha, colorbar=False)
        return surface * upper * lower
    return surface
