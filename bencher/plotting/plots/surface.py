from typing import Optional

import panel as pn
import logging
import xarray as xr

from bencher.bench_vars import ResultVar
from bencher.plotting.plot_filter import PlotFilter, PlotInput, VarRange, PltCntCfg
from bencher.plt_cfg import PltCfgBase
from bencher.plotting.plot_types import PlotTypes

from bencher.plotting_functions import wrap_long_time_labels
import holoviews as hv
from holoviews import opts


def plot_float_cnt_2(plt_cnt_cfg: PltCntCfg, rv: ResultVar, debug: bool) -> PltCfgBase:
    """A function for determining the plot settings if there are 2 float variable and updates the PltCfgBase

    Args:
        sns_cfg (PltCfgBase): See PltCfgBase definition
        plt_cnt_cfg (PltCntCfg): See PltCntCfg definition

    Returns:
        PltCfgBase: See PltCfgBase definition
    """
    xr_cfg = PltCfgBase()
    if plt_cnt_cfg.float_cnt == 2:
        logging.info(f"surface plot: {rv.name}")
        xr_cfg.plot_callback_xra = xr.plot.plot
        xr_cfg.x = plt_cnt_cfg.float_vars[0].name
        xr_cfg.y = plt_cnt_cfg.float_vars[1].name
        xr_cfg.xlabel = f"{xr_cfg.x} [{plt_cnt_cfg.float_vars[0].units}]"
        xr_cfg.ylabel = f"{xr_cfg.y} [{plt_cnt_cfg.float_vars[1].units}]"
        xr_cfg.zlabel = f"{rv.name} [{rv.units}]"
        xr_cfg.title = f"{rv.name} vs ({xr_cfg.x} and {xr_cfg.y})"

        if plt_cnt_cfg.cat_cnt >= 1:
            logging.info("surface plot with 1 categorical")
            xr_cfg.row = plt_cnt_cfg.cat_vars[0].name
            xr_cfg.num_rows = len(plt_cnt_cfg.cat_vars[0].values(debug))
        if plt_cnt_cfg.cat_cnt >= 2:
            logging.info("surface plot with 2> categorical")
            xr_cfg.col = plt_cnt_cfg.cat_vars[1].name
            xr_cfg.num_cols = len(plt_cnt_cfg.cat_vars[1].values(debug))
    return xr_cfg


class SurfacePlot:
    def surface_hv(self, pl_in: PlotInput) -> Optional[pn.panel]:
        """Given a benchCfg generate a 2D surface plot

        Args:
            bench_cfg (BenchCfg): description of benchmark
            rv (ParametrizedSweep): result variable to plot
            xr_cfg (PltCfgBase): config of x,y variables

        Returns:
            pn.pane.holoview: A 2d surface plot as a holoview in a pane
        """
        if False & PlotFilter(
            float_range=VarRange(2, 2),
            cat_range=VarRange(-1, None),
            vector_len=VarRange(1, 1),
            result_vars=VarRange(1, 1),
        ).matches(pl_in.plt_cnt_cfg):
            xr_cfg = plot_float_cnt_2(pl_in.plt_cnt_cfg, pl_in.rv, pl_in.bench_cfg.debug)
            # hv.extension("plotly")
            bench_cfg = pl_in.bench_cfg
            rv = pl_in.rv

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
                surface *= (
                    hv.Dataset(mean + std_dev).to(hv.Surface).opts(alpha=alpha, colorbar=False)
                )
                surface *= (
                    hv.Dataset(mean - std_dev).to(hv.Surface).opts(alpha=alpha, colorbar=False)
                )
            return pn.Column(surface, name=PlotTypes.surface_hv)

        return None
