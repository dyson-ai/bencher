from typing import Optional

import panel as pn
import plotly.graph_objs as go
import logging
import xarray as xr

from bencher.bench_cfg import BenchCfg
from bencher.bench_vars import ParametrizedSweep
from bencher.plotting.plot_filter import PlotFilter, PlotInput, VarRange, PltCntCfg
from bencher.plt_cfg import PltCfgBase
from bencher.plotting.plot_types import PlotTypes

from bencher.plotting_functions import wrap_long_time_labels


def plot_float_cnt_3(sns_cfg: PltCfgBase, plt_cnt_cfg: PltCntCfg, debug: bool) -> PltCfgBase:
    """A function for determining the plot settings if there are 2 float variable and updates the PltCfgBase

    Args:
        sns_cfg (PltCfgBase): See PltCfgBase definition
        plt_cnt_cfg (PltCntCfg): See PltCntCfg definition

    Returns:
        PltCfgBase: See PltCfgBase definition
    """
    xr_cfg = PltCfgBase(**sns_cfg.as_dict())

    if plt_cnt_cfg.float_cnt >= 3:
        logging.info("volume plot")
        sns_cfg.plot_callback = None  # all further plots are surfaces
        xr_cfg.plot_callback_xra = xr.plot.plot
        xr_cfg.x = plt_cnt_cfg.float_vars[0].name
        xr_cfg.y = plt_cnt_cfg.float_vars[1].name
        xr_cfg.z = plt_cnt_cfg.float_vars[2].name
        xr_cfg.xlabel = f"{xr_cfg.x} [{plt_cnt_cfg.float_vars[0].units}]"
        xr_cfg.ylabel = f"{xr_cfg.y} [{plt_cnt_cfg.float_vars[1].units}]"
        xr_cfg.zlabel = f"{xr_cfg.z} [{plt_cnt_cfg.float_vars[2].units}]"
        if plt_cnt_cfg.cat_cnt >= 1:
            logging.info("volume plot with 1 categorical")
            xr_cfg.row = plt_cnt_cfg.cat_vars[0].name
            xr_cfg.num_rows = len(plt_cnt_cfg.cat_vars[0].values(debug))
        if plt_cnt_cfg.cat_cnt >= 2:
            logging.info("volume plot with 2> categorical")
            xr_cfg.col = plt_cnt_cfg.cat_vars[1].name
            xr_cfg.num_cols = len(plt_cnt_cfg.cat_vars[1].values(debug))
    return xr_cfg


def plot_volume_plotly(
    bench_cfg: BenchCfg, rv: ParametrizedSweep, xr_cfg: PltCfgBase
) -> pn.pane.Plotly:
    """Given a benchCfg generate a 3D surface plot

    Args:
        bench_cfg (BenchCfg): description of benchmark
        rv (ParametrizedSweep): result variable to plot
        xr_cfg (PltCfgBase): config of x,y variables

    Returns:
        pn.pane.Plotly: A 3d volume plot as a holoview in a pane
    """

    bench_cfg = wrap_long_time_labels(bench_cfg)

    da = bench_cfg.ds[rv.name]

    mean = da.mean("repeat")

    opacity = 0.1

    meandf = mean.to_dataframe().reset_index()

    data = [
        go.Volume(
            x=meandf[xr_cfg.x],
            y=meandf[xr_cfg.y],
            z=meandf[xr_cfg.z],
            value=meandf[rv.name],
            isomin=meandf[rv.name].min(),
            isomax=meandf[rv.name].max(),
            opacity=opacity,
            surface_count=20,
        )
    ]

    layout = go.Layout(
        title=f"{rv.name} vs ({xr_cfg.x} vs {xr_cfg.y} vs {xr_cfg.z})",
        width=700,
        height=700,
        margin=dict(t=50, b=50, r=50, l=50),
        scene=dict(
            xaxis_title=xr_cfg.xlabel,
            yaxis_title=xr_cfg.ylabel,
            zaxis_title=xr_cfg.zlabel,
        ),
    )

    fig = dict(data=data, layout=layout)

    return pn.pane.Plotly(fig, name=PlotTypes.volume_plotly)


def plot_cone_plotly(
    bench_cfg: BenchCfg, rv: ParametrizedSweep, xr_cfg: PltCfgBase
) -> pn.pane.Plotly:
    """Given a benchCfg generate a 3D surface plot

    Args:
        bench_cfg (BenchCfg): description of benchmark
        rv (ParametrizedSweep): result variable to plot
        xr_cfg (PltCfgBase): config of x,y variables

    Returns:
        pn.pane.Plotly: A 3d volume plot as a holoview in a pane
    """

    bench_cfg = wrap_long_time_labels(bench_cfg)

    names = rv.index_names()

    # da = bench_cfg.ds[names[0]]

    opacity = 1.0

    df = bench_cfg.get_dataframe()

    print("size before removing zero size vectors", df.shape)
    df = df.loc[(df[names[0]] != 0.0) | (df[names[1]] != 0.0) | (df[names[2]] != 0.0)]
    print("size after removing zero size vectors", df.shape)

    data = [
        go.Cone(
            x=df[xr_cfg.x],
            y=df[xr_cfg.y],
            z=df[xr_cfg.z],
            u=df[names[0]],
            v=df[names[1]],
            w=df[names[2]],
            # sizemode="absolute",
            # sizeref=2,
            anchor="tail",
            opacity=opacity,
        )
    ]

    layout = go.Layout(
        title=f"{rv.name} vs ({xr_cfg.x} vs {xr_cfg.y} vs {xr_cfg.z})",
        autosize=True,
        width=700,
        height=700,
        margin=dict(t=50, b=50, r=50, l=50),
        scene=dict(
            xaxis_title=xr_cfg.xlabel,
            yaxis_title=xr_cfg.ylabel,
            zaxis_title=rv.name,
        ),
    )

    fig = dict(data=data, layout=layout)

    return pn.pane.Plotly(fig, name=PlotTypes.cone_plotly)


class VolumePlot:
    def volume_plotly(self, pl_in: PlotInput) -> Optional[pn.panel]:
        if PlotFilter(
            float_range=VarRange(3, 3),
            cat_range=VarRange(-1, 0),
            vector_len=VarRange(1, 1),
            result_vars=VarRange(1, 1),
        ).matches(pl_in.plt_cnt_cfg):
            sns_cfg = PltCfgBase()
            sns_cfg.y = pl_in.rv.name
            xr_cfg = plot_float_cnt_3(sns_cfg, pl_in.plt_cnt_cfg, pl_in.bench_cfg.debug)
            return plot_volume_plotly(pl_in.bench_cfg, pl_in.rv, xr_cfg)
        return None

    def cone_plotly(self, pl_in: PlotInput) -> Optional[pn.panel]:
        if PlotFilter(
            float_range=VarRange(3, 3),
            cat_range=VarRange(-1, 0),
            vector_len=VarRange(3, 3),
            result_vars=VarRange(1, 1),
        ).matches(pl_in.plt_cnt_cfg):
            sns_cfg = PltCfgBase()
            sns_cfg.y = pl_in.rv.name
            xr_cfg = plot_float_cnt_3(sns_cfg, pl_in.plt_cnt_cfg, pl_in.bench_cfg.debug)
            return plot_cone_plotly(pl_in.bench_cfg, pl_in.rv, xr_cfg)
        return None
