from __future__ import annotations
from enum import Enum, auto
import logging
from typing import List, Optional
import panel as pn
import holoviews as hv
import numpy as np
from param import Parameter
from functools import partial

from bencher.utils import hmap_canonical_input, get_nearest_coords
from bencher.results.bench_result_base import BenchResultBase
from bencher.plotting.plot_filter import PlotFilter, VarRange
from bencher.plotting.plt_cnt_cfg import PltCfgBase, PltCntCfg
from bencher.variables.results import ResultVar
import hvplot.xarray


hv.extension("bokeh", "plotly")

# width_heigh = {"width": 600, "height": 600, "tools": ["hover"]}

# hv.opts.defaults(
#     hv.opts.Curve(**width_heigh),
#     hv.opts.Points(**width_heigh),
#     hv.opts.Bars(**width_heigh),
#     hv.opts.Scatter(**width_heigh),
#     hv.opts.HeatMap(cmap="plasma", **width_heigh, colorbar=True),
#     # hv.opts.Surface(**width_heigh),
#     hv.opts.GridSpace(plot_size=400),
# )


class ReduceType(Enum):
    AUTO = auto()  # automatically determine the best way to reduce the dataset
    SQUEEZE = auto()  # remove any dimensions of length 1
    REDUCE = auto()  # get the mean and std dev of the the "repeat" dimension
    NONE = auto()  # don't reduce


class HoloviewResult(BenchResultBase):
    def to_hv_dataset(self, reduce: ReduceType = ReduceType.AUTO) -> hv.Dataset:
        """Generate a holoviews dataset from the xarray dataset.

        Args:
            reduce (ReduceType, optional): Optionally perform reduce options on the dataset.  By default the returned dataset will calculate the mean and standard devation over the "repeat" dimension so that the dataset plays nicely with most of the holoviews plot types.  Reduce.Sqeeze is used if there is only 1 repeat and you want the "reduce" variable removed from the dataset. ReduceType.None returns an unaltered dataset. Defaults to ReduceType.AUTO.

        Returns:
            hv.Dataset: results in the form of a holoviews dataset
        """

        if reduce == ReduceType.AUTO:
            reduce = ReduceType.REDUCE if self.bench_cfg.repeats > 1 else ReduceType.SQUEEZE

        vdims = [r.name for r in self.bench_cfg.result_vars]
        kdims = [i.name for i in self.bench_cfg.all_vars]
        match (reduce):
            case ReduceType.REDUCE:
                return hv.Dataset(self.ds, kdims=kdims, vdims=vdims).reduce(
                    ["repeat"], np.mean, np.std
                )
            case ReduceType.SQUEEZE:
                return hv.Dataset(self.ds.squeeze(drop=True), vdims=vdims)
            case _:
                return hv.Dataset(self.ds, kdims=kdims, vdims=vdims)

    def set_default_opts(width=600, height=600):
        width_heigh = {"width": width, "height": height, "tools": ["hover"]}
        # self.width = width
        # self.heigh = height
        hv.opts.defaults(
            hv.opts.Curve(**width_heigh),
            hv.opts.Points(**width_heigh),
            hv.opts.Bars(**width_heigh),
            hv.opts.Scatter(**width_heigh),
            hv.opts.HeatMap(cmap="plasma", **width_heigh, colorbar=True),
            # hv.opts.Surface(**width_heigh),
            hv.opts.GridSpace(plot_size=400),
        )
        return width_heigh

    def to(self, hv_type: hv.Chart, reduce: ReduceType = ReduceType.AUTO, **kwargs) -> hv.Chart:
        return self.to_hv_dataset(reduce).to(hv_type, **kwargs)

    def to_curve(self, reduce: ReduceType = ReduceType.AUTO, **kwargs) -> List[hv.Curve]:
        return self.overlay_plots(partial(self.to_curve_single, reduce=reduce, **kwargs))

    def overlay_plots(self, plot_callback: callable) -> Optional[hv.Overlay]:
        results = []
        for rv in self.bench_cfg.result_vars:
            res = plot_callback(rv)
            if res is not None:
                results.append(res)
        if len(results) > 0:
            return hv.Overlay(results).collate()
        return None

    def layout_plots(self, plot_callback: callable):
        if len(self.bench_cfg.result_vars) > 0:
            pt = hv.Overlay()
            for rv in self.bench_cfg.result_vars:
                pt += plot_callback(rv)
            return pt
        return plot_callback(self.bench_cfg.result_vars[0])

    def to_hvplot(self):
        ds = self.to_hv_dataset()

        # ds.data
        # print(type(ds.data))
        # print(ds.data)

        # return pn.pane.panel(ds.data.interactive())
        return None

    def to_curve_single(
        self, result_var: ResultVar, reduce: ReduceType = ReduceType.AUTO, **kwargs
    ) -> Optional[hv.Curve]:
        if PlotFilter(
            float_range=VarRange(1, None),
            cat_range=VarRange(0, None),
        ).matches(self.plt_cnt_cfg):
            title = self.to_plot_title()
            ds = self.to_hv_dataset(reduce)
            pt = ds.to(hv.Curve, vdims=[result_var.name], label=result_var.name).opts(
                title=title, **kwargs
            )
            if self.bench_cfg.repeats > 1:
                pt *= ds.to(hv.Spread).opts(alpha=0.2)
            return pt
        return None

    def to_error_bar(self) -> hv.Bars:
        return self.to_hv_dataset(ReduceType.REDUCE).to(hv.ErrorBars)

    def to_points(self, reduce: ReduceType = ReduceType.AUTO) -> hv.Points:
        ds = self.to_hv_dataset(reduce)
        pt = ds.to(hv.Points)
        if reduce:
            pt *= ds.to(hv.ErrorBars)
        return pt

    def to_scatter(self, **kwargs) -> Optional[hv.Scatter]:
        if PlotFilter(
            float_range=VarRange(0, 0), cat_range=VarRange(0, 1), repeats_range=VarRange(1, 1)
        ).matches(self.plt_cnt_cfg):
            return self.to_hv_dataset(ReduceType.REDUCE).to(hv.Scatter).opts(**kwargs)
        return None

    def to_scatter_jitter(self, **kwargs) -> Optional[hv.Scatter]:
        matches = PlotFilter(
            float_range=VarRange(0, 0),
            cat_range=VarRange(0, 1),
            repeats_range=VarRange(2, None),
            input_range=VarRange(1, None),
        ).matches(self.plt_cnt_cfg)
        if matches:
            ds = self.to_hv_dataset(ReduceType.NONE)
            pt = (
                ds.to(hv.Scatter)
                .opts(jitter=0.1)
                .overlay("repeat")
                .opts(show_legend=False, title=self.to_plot_title(), **kwargs)
            )
            return pt
        return None
        # return matches.to_panel()

    def to_bar(self, reduce: ReduceType = ReduceType.AUTO) -> hv.Bars:
        ds = self.to_hv_dataset(reduce)
        pt = ds.to(hv.Bars)
        if reduce:
            pt *= ds.to(hv.ErrorBars)
        return pt.opts(title=self.to_plot_title())

    def to_heatmap(self, reduce: ReduceType = ReduceType.AUTO, **kwargs) -> hv.HeatMap:
        return self.map_plots(partial(self.to_heatmap_single, reduce=reduce, **kwargs))

    def to_heatmap_single(
        self, result_var: ResultVar, reduce: ReduceType = ReduceType.AUTO, **kwargs
    ) -> hv.HeatMap:
        if PlotFilter(
            float_range=VarRange(2, None),
            cat_range=VarRange(0, None),
            input_range=VarRange(1, None),
        ).matches(self.plt_cnt_cfg):
            z = result_var
            title = f"{z.name} vs ("

            for iv in self.bench_cfg.input_vars:
                title += f" vs {iv.name}"
            title += ")"

            color_label = f"{z.name} [{z.units}]"

            return self.to(hv.HeatMap, reduce).opts(title=title, clabel=color_label,**kwargs)
        return None

    def to_heatmap_tap(
        self,
        result_var: ResultVar,
        reduce: ReduceType = ReduceType.AUTO,
        width=800,
        height=800,
        **kwargs,
    ):
        htmap = self.to_heatmap_single(result_var, reduce).opts(
            tools=["hover", "tap"], width=width, height=height
        )
        htmap_posxy = hv.streams.Tap(source=htmap, x=0, y=0)

        def tap_plot(x, y):
            kwargs[self.bench_cfg.input_vars[0].name] = x
            kwargs[self.bench_cfg.input_vars[1].name] = y
            return self.get_nearest_holomap(**kwargs).opts(width=width, height=height)

        tap_htmap = hv.DynamicMap(tap_plot, streams=[htmap_posxy])
        return htmap + tap_htmap

    def to_nd_layout(self, hmap_name: str) -> hv.NdLayout:
        print(self.bench_cfg.hmap_kdims)
        return hv.NdLayout(self.get_hmap(hmap_name), kdims=self.bench_cfg.hmap_kdims).opts(
            shared_axes=False, shared_datasource=False
        )

    def to_holomap(self, name: str = None) -> hv.HoloMap:
        return hv.HoloMap(self.to_nd_layout(name)).opts(shared_axes=False)

    def to_holomap_list(self, hmap_names: List[str] = None) -> hv.HoloMap:
        if hmap_names is None:
            hmap_names = [i.name for i in self.result_hmaps]
        col = pn.Column()
        for name in hmap_names:
            self.to_holomap(name)
        return col

    def get_nearest_holomap(self, name: str = None, **kwargs):
        canonical_inp = hmap_canonical_input(
            get_nearest_coords(self.ds, collapse_list=True, **kwargs)
        )
        return self.get_hmap(name)[canonical_inp].opts(framewise=True)

    def to_dynamic_map(self, name: str = None) -> hv.DynamicMap:
        """use the values stored in the holomap dictionary to populate a dynamic map. Note that this is much faster than passing the holomap to a holomap object as the values are calculated on the fly"""

        def cb(**kwargs):
            return self.get_hmap(name)[hmap_canonical_input(kwargs)].opts(
                framewise=True, shared_axes=False
            )

        kdims = []
        for i in self.bench_cfg.input_vars + [self.bench_cfg.iv_repeat]:
            kdims.append(i.as_dim(compute_values=True, debug=self.bench_cfg.debug))

        return hv.DynamicMap(cb, kdims=kdims)

    def to_grid(self, inputs=None):
        if inputs is None:
            inputs = self.bench_cfg.inputs_as_str()
        if len(inputs) > 2:
            inputs = inputs[:2]
        return self.to_holomap().grid(inputs)

    def to_table(self):
        return self.to(hv.Table, ReduceType.SQUEEZE)

    def to_surface_hv(self) -> pn.Row:
        return self.map_plots(self.to_surface_hv_single)

    def to_surface_hv_single(self, result_var: Parameter) -> Optional[pn.panel]:
        """Given a benchCfg generate a 2D surface plot

        Args:
            result_var (Parameter): result variable to plot

        Returns:
            pn.pane.holoview: A 2d surface plot as a holoview in a pane
        """
        if PlotFilter(
            float_range=VarRange(2, 2),
            cat_range=VarRange(0, None),
            vector_len=VarRange(1, 1),
            result_vars=VarRange(1, 1),
        ).matches(self.plt_cnt_cfg):
            xr_cfg = plot_float_cnt_2(self.plt_cnt_cfg, result_var, self.bench_cfg.debug)
            alpha = 0.3

            da = self.to_dataarray(result_var, False)
            mean = da.mean("repeat")

            # TODO a warning suggests setting this parameter, but it does not seem to help as expected, leaving here to fix in the future
            # hv.config.image_rtol = 1.0

            ds = hv.Dataset(mean)
            # try:
            # except Exception:
            #     return plot_surface_plotly(bench_cfg, rv, xr_cfg)

            try:
                surface = ds.to(hv.Surface, vdims=[result_var.name])
                surface = surface.opts(colorbar=True)
            except Exception as e:
                logging.warning(e)

            if self.bench_cfg.repeats > 1:
                std_dev = da.std("repeat")
                surface *= (
                    hv.Dataset(mean + std_dev)
                    .to(hv.Surface)
                    .opts(alpha=alpha, colorbar=False, backend="plotly")
                )
                surface *= (
                    hv.Dataset(mean - std_dev)
                    .to(hv.Surface)
                    .opts(alpha=alpha, colorbar=False, backend="plotly")
                )

            surface = surface.opts(
                width=800,
                height=800,
                zlabel=xr_cfg.zlabel,
                title=xr_cfg.title,
                backend="plotly",
            )

            if self.bench_cfg.render_plotly:
                hv.extension("plotly")
                out = surface
            else:
                # using render disabled the holoviews sliders :(
                out = hv.render(surface, backend="plotly")
            return pn.Column(out, name="surface_hv")

        return None

    # def plot_scatter2D_hv(self, rv: ParametrizedSweep) -> pn.pane.Plotly:
    # import plotly.express as px

    #     """Given a benchCfg generate a 2D scatter plot

    #     Args:
    #         bench_cfg (BenchCfg): description of benchmark
    #         rv (ParametrizedSweep): result variable to plot

    #     Returns:
    #         pn.pane.Plotly: A 3d volume plot as a holoview in a pane
    #     """

    #     # bench_cfg = wrap_long_time_labels(bench_cfg)
    #     self.ds.drop_vars("repeat")

    #     df = self.to_pandas()

    #     names = rv.index_names()

    #     return px.scatter(
    #         df, x=names[0], y=names[1], marginal_x="histogram", marginal_y="histogram"
    #     )


HoloviewResult.set_default_opts()


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
