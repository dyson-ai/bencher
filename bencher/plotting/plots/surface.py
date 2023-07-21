from typing import Optional

import panel as pn
import plotly.graph_objs as go
import logging
import xarray as xr

from bencher.bench_cfg import BenchCfg
from bencher.bench_vars import ParametrizedSweep
from bencher.plotting.plot_filter import PlotFilter, PlotInput, VarRange, PltCntCfg
from bencher.plt_cfg import PltCfgBase, BenchPlotter
from bencher.plotting.plot_types import PlotTypes

from bencher.plotting_functions import wrap_long_time_labels, plot_surface_holo
import holoviews as hv
from holoviews import opts


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
        if PlotFilter(
            float_range=VarRange(2, 2),
            cat_range=VarRange(-1, None),
            vector_len=VarRange(1, 1),
            result_vars=VarRange(1, 1),
        ).matches(pl_in.plt_cnt_cfg):
            xr_cfg = BenchPlotter.plot_float_cnt_2(
                pl_in.plt_cnt_cfg, pl_in.rv, pl_in.bench_cfg.debug
            )
            hv.extension("plotly")
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
                upper = hv.Dataset(mean + std_dev).to(hv.Surface).opts(alpha=alpha, colorbar=False)
                lower = hv.Dataset(mean - std_dev).to(hv.Surface).opts(alpha=alpha, colorbar=False)
                return surface * upper * lower
            return pn.panel(surface, name=PlotTypes.surface_hv)

        return None
