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
                    row.append(self.to_video_grid_ds(ds, rv, input_order, reverse, **kwargs))
            return row
        return matches_res.to_panel()

    def to_video_grid_ds(
        self,
        dataset: xr.Dataset,
        result_var: Parameter,
        input_order: List[str] = None,
        reverse: bool = True,
        video_controls: VideoControls = None,
        **kwargs,
    ):
        vr = VideoWriter()

        img_array = dataset[result_var.name].to_numpy()

        fn = vr.write_grid2d(img_array)

        if fn is not None:
            if video_controls is None:
                video_controls = VideoControls()
            vid = video_controls.video_container(fn, **kwargs)
            return vid
        return None

    def _to_video_ds(
        self,
        dataset: xr.Dataset,
        plot_callback: callable = None,
        target_dimension=0,
        result_var=None,
        **kwargs,
    ) -> pn.panel:
        num_dims = len(dataset.sizes)
        dims = list(d for d in dataset.sizes)

        print("np")
        print(dataset[result_var.name].to_numpy())

        # exit()

        # plot_callback = lambda x:x

        time_dim_delta = 0
        if self.bench_cfg.over_time:
            time_dim_delta = 0

        if num_dims > (target_dimension + time_dim_delta) and num_dims != 0:
            dim_sel = dims[-1]
            outer_container = []
            for i in range(dataset.sizes[dim_sel]):
                sliced = dataset.isel({dim_sel: i})

                panes = self._to_video_ds(
                    sliced,
                    plot_callback=plot_callback,
                    target_dimension=target_dimension,
                    horizontal=len(sliced.sizes) <= target_dimension + 1,
                    result_var=result_var,
                )
                width = num_dims - target_dimension

                outer_container.append(panes)
                # outer_container.append(pn.Row(inner_container, align="center"))
            for c in outer_container:
                c[0].width = max_len * 7
        else:
            return plot_callback(dataset=dataset, result_var=result_var, **kwargs)

        return outer_container
