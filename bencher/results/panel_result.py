from typing import Optional, Any
from functools import partial
import panel as pn
import xarray as xr
from param import Parameter
from bencher.results.bench_result_base import BenchResultBase, ReduceType
from bencher.results.video_result import VideoControls
from bencher.variables.results import (
    ResultReference,
    PANEL_TYPES,
)


class PanelResult(BenchResultBase):
    def to_video(self, result_var: Parameter = None, **kwargs):
        vc = VideoControls()
        return pn.Column(
            vc.video_controls(),
            self.to_panes(result_var=result_var, container=vc.video_container, **kwargs),
        )

    def zero_dim_da_to_val(self, da_ds: xr.DataArray | xr.Dataset) -> Any:
        # todo this is really horrible, need to improve
        dim = None
        if isinstance(da_ds, xr.Dataset):
            dim = list(da_ds.keys())[0]
            da = da_ds[dim]
        else:
            da = da_ds

        for k in da.coords.keys():
            dim = k
            break
        if dim is None:
            return da_ds.values.squeeze().item()
        return da.expand_dims(dim).values[0]

    def ds_to_container(
        self, dataset: xr.Dataset, result_var: Parameter, container, **kwargs
    ) -> Any:
        val = self.zero_dim_da_to_val(dataset[result_var.name])
        if isinstance(result_var, ResultReference):
            ref = self.object_index[val]
            val = ref.obj
            if ref.container is not None:
                return ref.container(val, **kwargs)
        if container is not None:
            return container(val, styles={"background": "white"}, **kwargs)
        return val

    def to_panes(
        self, result_var: Parameter = None, target_dimension: int = 0, container=None, **kwargs
    ) -> Optional[pn.pane.panel]:
        if container is None:
            container = pn.pane.panel
        return self.map_plot_panes(
            partial(self.ds_to_container, container=container),
            hv_dataset=self.to_hv_dataset(ReduceType.SQUEEZE),
            target_dimension=target_dimension,
            result_var=result_var,
            result_types=PANEL_TYPES,
            **kwargs,
        )
