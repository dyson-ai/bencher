from bencher.utils import params_to_str
from typing import Optional, List
import itertools
import panel as pn
import xarray as xr
from param import Parameter
from bencher.results.bench_result_base import BenchResultBase, ReduceType
from bencher.variables.results import ResultImage
from bencher.plotting.plot_filter import VarRange, PlotFilter
from bencher.utils import callable_name, listify
from bencher.video_writer import VideoWriter
from bencher.results.float_formatter import FormatFloat
from bencher.results.video_result import VideoControls
from bencher.utils import int_to_col
from bencher.results.composable_container.composable_container_video import (
    ComposableContainerVideo,
    ComposeType,
)
from copy import deepcopy


class VideoSummaryResult(BenchResultBase):
    def to_video_summary(
        self,
        result_var: Parameter = None,
        input_order: List[str] = None,
        reverse: bool = True,
        result_types=(ResultImage,),
        **kwargs,
    ) -> Optional[pn.panel]:
        plot_filter = PlotFilter(
            float_range=VarRange(0, None),
            cat_range=VarRange(0, None),
            panel_range=VarRange(1, None),
        )
        matches_res = plot_filter.matches_result(
            self.plt_cnt_cfg, callable_name(self.to_video_summary_ds)
        )

        # video_controls = VideoControls()
        if matches_res.overall:
            ds = self.to_dataset(ReduceType.SQUEEZE)
            row = pn.Row()
            for rv in self.get_results_var_list(result_var):
                if isinstance(rv, result_types):
                    row.append(self.to_video_summary_ds(ds, rv, input_order, reverse, **kwargs))
            return row
        return matches_res.to_panel()

    def to_video_summary_ds(
        self,
        dataset: xr.Dataset,
        result_var: Parameter,
        input_order: List[str] = None,
        reverse: bool = True,
        video_controls: VideoControls = None,
        **kwargs,
    ):
        vr = VideoWriter()
        da = dataset[result_var.name]

        if input_order is None:
            input_order = list(da.dims)
        else:
            input_order = params_to_str(input_order)
        if reverse:
            input_order = list(reversed(input_order))

        inputs_produc = [da.coords[i].values for i in input_order]

        for index in itertools.product(*inputs_produc):
            lookup = dict(zip(input_order, index))
            val = da.loc[lookup].item()
            index = listify(index)
            for i in range(len(index)):
                if isinstance(index[i], (int, float)):
                    index[i] = FormatFloat()(index[i])
            label = ", ".join(f"{a[0]}={a[1]}" for a in list(zip(input_order, index)))
            if val is not None:
                vr.append_file(val, label)
        fn = vr.write_png()
        if fn is not None:
            if video_controls is None:
                video_controls = VideoControls()
            vid = video_controls.video_container(fn, **kwargs)
            return vid

        return None

    def to_video_grid(
        self,
        result_var: Parameter = None,
        result_types=(ResultImage,),
        **kwargs,
    ) -> Optional[pn.panel]:
        plot_filter = PlotFilter(
            float_range=VarRange(0, None),
            cat_range=VarRange(0, None),
            panel_range=VarRange(1, None),
            input_range=VarRange(1, None),
        )
        matches_res = plot_filter.matches_result(
            self.plt_cnt_cfg, callable_name(self.to_video_grid_ds)
        )
        if matches_res.overall:
            ds = self.to_dataset(ReduceType.SQUEEZE)
            row = pn.Row()
            for rv in self.get_results_var_list(result_var):
                if isinstance(rv, result_types):
                    row.append(self.to_video_grid_ds(ds, rv, **kwargs))
            return row
        return matches_res.to_panel()

    def to_video_grid_ds(
        self,
        dataset: xr.Dataset,
        result_var: Parameter,
        reverse=True,
        time_sequence_dimension=0,
        video_controls: VideoControls = None,
        **kwargs,
    ):
        vr = VideoWriter()

        if True:

            cvc = self._to_video_panes_ds(
                dataset,
                self.plot_cb,
                target_dimension=0,
                time_sequence_dimension=time_sequence_dimension,
                compose_method=ComposeType.right,
                result_var=result_var,
                reverse=reverse,
                **kwargs,
            )
        else:
            da = dataset[result_var.name]
            input_order = list(da.dims)
            if reverse:
                input_order = list(reversed(input_order))
            inputs_produc = [da.coords[i].values for i in input_order]

            ccv = ComposableContainerVideo(var_name="lol")

            for index in itertools.product(*inputs_produc):
                lookup = dict(zip(input_order, index))
                val = da.loc[lookup].item()
                if val is not None:
                    ccv.append(val)
            cvc = ccv.render(compose_method=ComposeType.right)
            cvcd = ccv.render(compose_method=ComposeType.down)

            ccv2 = ComposableContainerVideo(compose_method=ComposeType.sequence)
            ccv2.append(cvc)
            ccv2.append(cvcd)

            cvc = ccv2.render()
            print(cvc.duration)

        fn = vr.write_video_raw(cvc)

        if fn is not None:
            if video_controls is None:
                video_controls = VideoControls()
            vid = video_controls.video_container(fn, **kwargs)
            return vid
        return None

    def plot_cb(self, dataset, result_var, **kwargs):
        val = self.ds_to_container(dataset, result_var, container=None, **kwargs)
        return val

    def dataset_to_compose_list(
        self, dataset, first_compose_method=ComposeType.right, time_sequence_dimension=0
    ):
        num_dims = len(dataset.sizes)
        # print(dataset)
        # print(dataset.sizes)
        compose_method_list = [first_compose_method]
        for i in range(num_dims - 1):
            compose_method_list.append(ComposeType.flip(compose_method_list[-1]))

        # print(compose_method_list)
        # exit()
        # compose_method_list.insert(0,ComposeType.sequence)
        compose_method_list.append(ComposeType.sequence)

        for i in range(time_sequence_dimension + 1):
            compose_method_list[i] = ComposeType.sequence

        return compose_method_list

    def _to_video_panes_ds(
        self,
        dataset: xr.Dataset,
        plot_callback: callable = None,
        target_dimension=0,
        compose_method=ComposeType.right,
        compose_method_list=None,
        result_var=None,
        time_sequence_dimension=0,
        root_dimensions=None,
        reverse=False,
        **kwargs,
    ) -> pn.panel:
        num_dims = len(dataset.sizes)
        dims = list(d for d in dataset.sizes)
        if reverse:
            dims = list(reversed(dims))

        if root_dimensions is None:
            root_dimensions = num_dims

        if compose_method_list is None:
            compose_method_list = self.dataset_to_compose_list(
                dataset, compose_method, time_sequence_dimension=time_sequence_dimension
            )
            print("first compose")
            print(compose_method_list)

        compose_method_list_pop = deepcopy(compose_method_list)
        compose_method = compose_method_list_pop.pop()

        if num_dims > (target_dimension) and num_dims != 0:
            selected_dim = dims[-1]
            # print(f"selected dim {selected_dim}")
            dim_color = int_to_col(num_dims - 2, 0.05, 1.0)
            # sliced = dataset.isel({selected_dim: i})
            # label_val = sliced.coords[selected_dim].values.item()

            outer_container = ComposableContainerVideo(
                name=" vs ".join(dims),
                background_col=dim_color,
                compose_method=compose_method,
                # var_name=selected_dim,
                # var_value=label_val,
            )
            max_len = 0
            for i in range(dataset.sizes[selected_dim]):
                sliced = dataset.isel({selected_dim: i})
                label_val = sliced.coords[selected_dim].values.item()
                inner_container = ComposableContainerVideo(
                    outer_container.name,
                    var_name=selected_dim,
                    var_value=label_val,
                    compose_method=compose_method,
                )

                panes = self._to_video_panes_ds(
                    sliced,
                    plot_callback=plot_callback,
                    target_dimension=target_dimension,
                    compose_method_list=compose_method_list_pop,
                    result_var=result_var,
                    root_dimensions=root_dimensions,
                    time_sequence_dimension=time_sequence_dimension,
                )
                inner_container.append(panes)

                if inner_container.label_len > max_len:
                    max_len = inner_container.label_len

                rendered = inner_container.render()
                outer_container.append(rendered)
            concat_with_time = (root_dimensions - num_dims) <= time_sequence_dimension
            print(f"Num DIMS: {num_dims}, {dims}")
            print(f"Distance from root: {root_dimensions - num_dims}")
            print(
                f"Distance from time_seq tim{root_dimensions - num_dims -time_sequence_dimension}"
            )
            print(f"Time seq: {time_sequence_dimension}")
            print(f"Concat_time: {concat_with_time}")
            concat_method = None
            if concat_with_time:
                concat_method = ComposeType.sequence
            print(compose_method_list_pop)
            print(f"rendering with {compose_method}")
            return outer_container.render(compose_method)
        return plot_callback(dataset=dataset, result_var=result_var, **kwargs)
