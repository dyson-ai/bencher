
import xarray as xr
import holoviews as hv
import panel as pn
from collections import OrderedDict
from sortedcontainers import SortedDict
from typing import List, Iterable, Callable, Any
import itertools
from more_itertools import chunked
import numpy as np

def values_from_dim(dim: hv.Dimension, samples):
    return np.linspace(dim.range[0], dim.range[1], samples)


class DimensionGrid:
    def __init__(self, dims: List[hv.Dimension], samples: int | Iterable[int]) -> None:
        self.dims = dims
        if not isinstance(samples, Iterable):
            samples = [samples] * len(dims)
        self.values = [values_from_dim(d, s) for d, s in zip(self.dims, samples)]
        self.coord_len = [len(v) for v in self.values]
        self.dim_names = [d.name for d in dims]
        # self.coords = OrderedDict([(d.name, d.values) for d in dims])
        self.coords = OrderedDict([(d.name, v) for d, v in zip(dims, self.values)])

    def inputs_iterable(self):
        return itertools.product(*self.values)

    def inputs_dict(self) -> list[SortedDict]:
        return [SortedDict(zip(self.dim_names, i)) for i in self.inputs_iterable()]

    def to_datarray(self, data: List[Any], name: str) -> xr.DataArray:
        da = xr.DataArray(data=data, dims=self.dim_names, coords=self.coords, name=name)
        for d in self.dims:
            attrs = da[d.name].attrs
            attrs["units"] = d.unit
            attrs["longname"] = d.name
            attrs["description"] = d.label
        return da

    def to_hv_dataset(self, data: List[Any], name: str) -> hv.Dataset:
        return hv.Dataset(self.to_datarray(data, name))

    def apply_fn(self, build_tensor_cb: Callable, process_tensor_cb: Callable, chunk_size=None):
        inputs = self.inputs_iterable()
        outputs = []
        chunk_num=1
        for chunk in chunked(inputs, chunk_size):
            input_dict = []
            for i in chunk:
                inp = dict(zip(self.dim_names, i))
                input_dict.append(build_tensor_cb(**inp))
            print(f"chunk {chunk_num} size: {len(input_dict)}")
            chunk_num+=1
            res = process_tensor_cb(input_dict).cpu().numpy()
            outputs.append(res)
        combined = np.vstack(outputs)
        return combined.reshape(self.coord_len)
