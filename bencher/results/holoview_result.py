from __future__ import annotations
from enum import Enum, auto
from typing import List
import panel as pn
import xarray as xr
import holoviews as hv
import numpy as np
from bencher.utils import hmap_canonical_input, get_nearest_coords
from bencher.results.bench_result_base import BenchResultBase


class ReduceType(Enum):
    AUTO = auto()
    SQUEEZE = auto()
    REDUCE = auto()
    NONE = auto()


class HoloviewResult(BenchResultBase):
    def to_hv_dataset(self, reduce: ReduceType = ReduceType.AUTO) -> hv.Dataset:
        """Generate a holoviews dataset from the xarray dataset.

        Args:
            reduce (ReduceType, optional): Optionally perform reduce options on the dataset.  By default the returned dataset will calculate the mean and standard devation over the "repeat" dimension so that the dataset plays nicely with most of the holoviews plot types.  Reduce.Sqeeze is used if there is only 1 repeat and you want the "reduce" variable removed from the dataset. ReduceType.None returns an unaltered dataset. Defaults to ReduceType.AUTO.

        Returns:
            hv.Dataset: results in the form of a holoviews dataset
        """
        ds = convert_dataset_bool_dims_to_str(self.ds)

        if reduce == ReduceType.AUTO:
            reduce = ReduceType.REDUCE if self.repeats > 1 else ReduceType.SQUEEZE

        result_vars_str = [r.name for r in self.result_vars]
        kdims = [i.name for i in self.input_vars]
        kdims.append("repeat")  # repeat is always used
        hvds = hv.Dataset(ds, kdims=kdims, vdims=result_vars_str)
        if reduce == ReduceType.REDUCE:
            return hvds.reduce(["repeat"], np.mean, np.std)
        if reduce == ReduceType.SQUEEZE:
            return hv.Dataset(ds.squeeze("repeat", drop=True), vdims=result_vars_str)
        return hvds

    def to(self, hv_type: hv.Chart, reduce: ReduceType = ReduceType.AUTO, **kwargs) -> hv.Chart:
        return self.to_hv_dataset(reduce).to(hv_type, **kwargs)

    def to_curve(self, reduce: ReduceType = ReduceType.AUTO) -> hv.Curve:
        title = f"{self.result_vars[0].name} vs {self.input_vars[0].name}"
        ds = self.to_hv_dataset(reduce)
        pt = ds.to(hv.Curve).opts(title=title)
        if self.repeats > 1:
            pt *= ds.to(hv.Spread).opts(alpha=0.2)
        return pt

    def to_error_bar(self) -> hv.Bars:
        return self.to_hv_dataset(ReduceType.REDUCE).to(hv.ErrorBars)

    def to_points(self, reduce: ReduceType = ReduceType.AUTO) -> hv.Points:
        ds = self.to_hv_dataset(reduce)
        pt = ds.to(hv.Points)
        if reduce:
            pt *= ds.to(hv.ErrorBars)
        return pt

    def to_scatter(self):
        return self.to_hv_dataset(ReduceType.REDUCE).to(hv.Scatter)

    def to_scatter_jitter(self) -> hv.Scatter:
        ds = self.to_hv_dataset(ReduceType.NONE)
        pt = ds.to(hv.Scatter).opts(jitter=0.1).overlay("repeat").opts(show_legend=False)
        return pt

    def to_bar(self, reduce: ReduceType = ReduceType.AUTO) -> hv.Bars:
        ds = self.to_hv_dataset(reduce)
        pt = ds.to(hv.Bars)
        if reduce:
            pt *= ds.to(hv.ErrorBars)
        return pt

    def to_heatmap(self, reduce: ReduceType = ReduceType.AUTO, **kwargs) -> hv.HeatMap:
        z = self.result_vars[0]
        title = f"{z.name} vs ({self.input_vars[0].name}"

        for iv in self.input_vars[1:]:
            title += f" vs {iv.name}"
        title += ")"

        color_label = f"{z.name} [{z.units}]"

        return self.to(hv.HeatMap, reduce, **kwargs).opts(title=title, clabel=color_label)

    def to_heatmap_tap(self, reduce: ReduceType = ReduceType.AUTO, width=800, height=800, **kwargs):
        htmap = self.to_heatmap(reduce).opts(tools=["hover", "tap"], width=width, height=height)
        htmap_posxy = hv.streams.Tap(source=htmap, x=0, y=0)

        def tap_plot(x, y):
            kwargs[self.input_vars[0].name] = x
            kwargs[self.input_vars[1].name] = y
            return self.get_nearest_holomap(**kwargs).opts(width=width, height=height)

        tap_htmap = hv.DynamicMap(tap_plot, streams=[htmap_posxy])
        return htmap + tap_htmap

    def to_nd_layout(self, hmap_name: str) -> hv.NdLayout:
        print(self.hmap_kdims)
        return hv.NdLayout(self.get_hmap(hmap_name), kdims=self.hmap_kdims).opts(
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
        for i in self.input_vars + [self.bench_cfg.iv_repeat]:
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


def convert_dataset_bool_dims_to_str(dataset: xr.Dataset) -> xr.Dataset:
    """Given a dataarray that contains boolean coordinates, conver them to strings so that holoviews loads the data properly

    Args:
        dataarray (xr.DataArray): dataarray with boolean coordinates

    Returns:
        xr.DataArray: dataarray with boolean coordinates converted to strings
    """
    bool_coords = {}
    for c in dataset.coords:
        if dataset.coords[c].dtype == bool:
            bool_coords[c] = [str(vals) for vals in dataset.coords[c].values]

    if len(bool_coords) > 0:
        return dataset.assign_coords(bool_coords)
    return dataset
