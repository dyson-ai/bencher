from typing import Optional
from functools import partial
import panel as pn
import xarray as xr
from bencher.utils import int_to_col, color_tuple_to_css
from bencher.variables.results import ResultVar
from bencher.results.bench_result_base import BenchResultBase
from bencher.variables.parametrised_sweep import ParametrizedSweep
from bencher.variables.results import ResultImage, ResultVideo
from bencher.plotting.plot_filter import PlotFilter, VarRange


class PanelResult(BenchResultBase):
    def to_video(self, **kwargs):
        return self.map_plots(partial(self.to_video_single, **kwargs))

    def to_video_single(self, result_var: ParametrizedSweep, **kwargs) -> Optional[pn.pane.PNG]:
        if isinstance(result_var, ResultVideo):
            vid_p = []

            def create_video(vid):  # pragma: no cover
                vid = pn.pane.Video(vid, autoplay=True, **kwargs)
                vid.loop = True
                vid_p.append(vid)
                return vid

            panes = self.to_panes(create_video)

            def play_vid(_):  # pragma: no cover
                for r in vid_p:
                    r.paused = False
                    r.loop = False

            def pause_vid(_):  # pragma: no cover
                for r in vid_p:
                    r.paused = True

            def reset_vid(_):  # pragma: no cover
                for r in vid_p:
                    r.paused = False
                    r.time = 0

            def loop_vid(_):  # pragma: no cover
                for r in vid_p:
                    r.paused = False
                    r.time = 0
                    r.loop = True

            button_names = ["Play Videos", "Pause Videos", "Loop Videos", "Reset Videos"]
            buttom_cb = [play_vid, pause_vid, reset_vid, loop_vid]
            buttons = pn.Row()

            for name, cb in zip(button_names, buttom_cb):
                button = pn.widgets.Button(name=name)
                pn.bind(cb, button, watch=True)
                buttons.append(button)

            return pn.Column(buttons, panes)
        return None

    def to_image(self) -> pn.Row():
        return self.map_plots(self.to_image_single)

    def to_image_single(
        self, result_var: ParametrizedSweep, container=pn.pane.PNG
    ) -> Optional[pn.pane.PNG]:
        if isinstance(result_var, ResultImage):
            xr_dataset = self.to_hv_dataset()
            plot_callback = partial(self.da_to_container, container=pn.pane.PNG)
            return self.to_panes_multi_panel(
                xr_dataset, result_var, plot_callback=plot_callback, target_dimension=0
            )

        return None

    def zero_dim_da_to_val(self, da: xr.DataArray):
        for k in da.coords.keys():
            dim = k
            break
        return da.expand_dims(dim).values[0]

    def da_to_container(self, da: xr.DataArray, container):
        val = self.zero_dim_da_to_val(da)
        return container(val, styles={"background": "white"})

    def to_panes(self, container=pn.pane.panel, **kwargs) -> Optional[pn.pane.panel]:
        matches_res = PlotFilter(
            float_range=VarRange(0, None),
            cat_range=VarRange(0, None),
            # panel_range=VarRange(1, None),
        ).matches_result(self.plt_cnt_cfg, "to_panes")
        if matches_res.overall:
            return self.map_plots(partial(self.to_panes_single, container=container, **kwargs))
        return matches_res.to_panel()

    def to_panes_multi(
        self, plot_callback, result_var: ResultVar = None, target_dimension=1, **kwargs
    ) -> Optional[pn.pane.panel]:
        if result_var is None:
            result_var = self.bench_cfg.result_vars[0]
        # xr_dataarray = self.to_dataarray(result_var)

        xr_dataarray = self.to_hv_dataset().data[result_var.name]

        return self._to_panes_da(
            xr_dataarray,
            plot_callback=plot_callback,
            target_dimension=target_dimension,
            **kwargs,
        )

    def to_da(self, da):
        return da

    def to_panes_multi2(
        self, xr_dataset, result_var, plot_callback=None, target_dimension=1, **kwargs
    ):
        if result_var is None:
            result_var = self.bench_cfg.result_vars[0]

        xr_dataarray = xr_dataset.data[result_var.name]

        return self._to_panes_da(
            xr_dataarray,
            plot_callback=plot_callback,
            target_dimension=target_dimension,
            horizontal=len(xr_dataarray.dims) == target_dimension,
            **kwargs,
        )

    def to_panes_multi_panel(
        self, xr_dataset, result_var, plot_callback=None, target_dimension=1, **kwargs
    ):
        if result_var is None:
            result_var = self.bench_cfg.result_vars[0]

        xr_dataarray = xr_dataset.data[result_var.name]

        return self._to_panes_da(
            xr_dataarray,
            plot_callback=plot_callback,
            target_dimension=target_dimension,
            horizontal=len(xr_dataarray.dims) <= target_dimension + 1,
            **kwargs,
        )

    def to_panes_single(
        self, result_var: ResultVar, container=pn.pane.panel, **kwargs
    ) -> Optional[pn.pane.panel]:
        xr_dataarray = self.to_dataarray(result_var)
        return self._to_panes(
            xr_dataarray, len(xr_dataarray.dims) == 1, container=container, **kwargs
        )

    def to_reference_single(self, obj, container=None):
        obj_item = self.object_index[obj].obj
        if container is not None:
            return container(obj_item)
        return obj_item

    def to_reference_single_da(self, da: xr.DataArray, container=None):
        val = self.zero_dim_da_to_val(da)
        obj_item = self.object_index[val].obj
        if container is not None:
            return container(obj_item)
        return obj_item

    def to_references_old(self, container=None):
        return self.map_plots(
            partial(
                self.to_panes_single,
                container=partial(self.to_reference_single, container=container),
            )
        )

    # def da_to_reference(self, da: xr.DataArray, container):
    #     val = self.zero_dim_da_to_val(da)
    #     return container(val, styles={"background": "white"})

    def to_references(self, container=None, **kwargs):
        xr_dataset = self.to_hv_dataset()
        plot_callback = partial(self.to_reference_single_da, container=container, **kwargs)
        return self.to_panes_multi_panel(
            xr_dataset, None, plot_callback=plot_callback, target_dimension=0
        )

    def _to_panes(
        self, da: xr.DataArray, last_item=False, container=pn.pane.panel, in_card=True, **kwargs
    ) -> pn.panel:
        num_dims = len(da.dims)
        if num_dims > 1:
            dim_sel = da.dims[-1]

            dim_color = color_tuple_to_css(int_to_col(num_dims - 2, 0.05, 1.0))

            background_col = dim_color
            name = " vs ".join(da.dims)
            outer_container = pn.Card(
                title=name,
                name=name,
                styles={"background": background_col},
                header_background=dim_color,
            )

            # todo remove this pre calculation and let panel work out the right sizes
            padded_labels = []
            sliced_da = []
            max_label_size = 0
            for i in range(da.sizes[dim_sel]):
                sliced = da.isel({dim_sel: i})
                padded_labels.append(
                    f"{dim_sel}={sliced.coords[dim_sel].values}",
                )
                label_size = len(padded_labels[-1])
                if label_size > max_label_size:
                    max_label_size = label_size
                sliced_da.append(sliced)

            for i in range(da.sizes[dim_sel]):
                sliced = sliced_da[i]

                panes = self._to_panes(
                    sliced,
                    i == da.sizes[dim_sel] - 1,
                    container=container,
                    in_card=False,
                )
                label = padded_labels[i].rjust(max_label_size, " ")
                side = pn.pane.Markdown(
                    f"{label}", align=("end", "center"), width=max_label_size * 8
                )

                outer_container.append(pn.Row(side, panes))
        else:
            name = f"{da.dims[0]} vs {da.name}"
            if in_card:
                outer_container = pn.Card(title=name, name=name)
            else:
                outer_container = pn.Column(name=name)

            inner = pn.Row(styles={"background": "white"})
            align = ("center", "start")

            if last_item:
                dim_id = da.dims[0]
                for val, label in zip(da.values, da.coords[dim_id].values):
                    col = pn.Column()
                    col.append(container(val, **kwargs))
                    col.append(pn.pane.Markdown(f"{da.dims[0]}={label}", align=align))
                    # styles={"border-top": "1px solid grey"},sizing_mode="stretch_width"
                    inner.append(col)
            else:
                for val in da.values:
                    inner.append(container(val, **kwargs))
            outer_container.append(inner)

        return outer_container

    def _to_panes_da(
        self,
        da: xr.DataArray,
        plot_callback=pn.pane.panel,
        target_dimension=1,
        horizontal=False,
        **kwargs,
    ) -> pn.panel:
        num_dims = len(da.dims)
        print(f"num_dims: {num_dims}, horizontal: {horizontal}, target: {target_dimension}")

        if num_dims > target_dimension and num_dims != 0:
            dim_sel = da.dims[-1]

            # vertical=len(sliced.dims) == target_dimension,

            dim_color = color_tuple_to_css(int_to_col(num_dims - 2, 0.05, 1.0))

            background_col = dim_color
            name = " vs ".join(da.dims)

            # header_background=dim_color,
            container_args = dict(name=name, styles={"background": background_col})
            outer_container = (
                pn.Row(**container_args) if horizontal else pn.Column(**container_args)
            )

            for i in range(da.sizes[dim_sel]):
                sliced = da.isel({dim_sel: i})
                label = f"{dim_sel}={sliced.coords[dim_sel].values}"

                panes = self._to_panes_da(
                    sliced,
                    plot_callback=plot_callback,
                    target_dimension=target_dimension,
                    horizontal=len(sliced.dims) <= target_dimension + 1,
                )
                width = num_dims - target_dimension
                if horizontal:
                    inner_container = pn.Column(styles={"border": f"{width}px solid grey"})
                    align = ("center", "center")
                else:
                    inner_container = pn.Row(styles={"border": f"{width}px solid grey"})
                    align = ("end", "center")

                side = pn.pane.Markdown(f"{label}", align=align)

                inner_container.append(side)
                inner_container.append(panes)
                outer_container.append(inner_container)
        else:
            return plot_callback(da=da, **kwargs)

        return outer_container

    def _to_panes_ds(
        self,
        ds: xr.Dataset,
        plot_callback=pn.pane.panel,
        target_dimension=1,
        vertical=True,
        **kwargs,
    ) -> pn.panel:
        num_dims = len(ds.dims)
        if num_dims > target_dimension:
            dim_sel = ds.dims[-1]

            # vertical=len(sliced.dims) == target_dimension,

            dim_color = color_tuple_to_css(int_to_col(num_dims - 2, 0.05, 1.0))

            background_col = dim_color
            name = " vs ".join(ds.dims)

            # header_background=dim_color,
            container_args = dict(name=name, styles={"background": background_col})
            outer_container = pn.Column(**container_args) if vertical else pn.Row(**container_args)

            for i in range(ds.sizes[dim_sel]):
                sliced = ds.isel({dim_sel: i})
                label = f"{dim_sel}={sliced.coords[dim_sel].values}"

                panes = self._to_panes_ds(
                    sliced,
                    plot_callback=plot_callback,
                    target_dimension=target_dimension,
                    vertical=len(sliced.dims) == target_dimension,
                )
                width = num_dims - target_dimension
                if vertical:
                    inner_container = pn.Row(styles={"border": f"{width}px solid grey"})
                    align = ("end", "center")
                else:
                    inner_container = pn.Column(styles={"border": f"{width}px solid grey"})
                    align = ("center", "center")
                side = pn.pane.Markdown(f"{label}", align=align)

                inner_container.append(side)
                inner_container.append(panes)
                outer_container.append(inner_container)
        else:
            return plot_callback(da=ds, **kwargs)

        return outer_container
