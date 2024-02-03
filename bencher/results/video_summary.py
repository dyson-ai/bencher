from bencher.utils import params_to_str
from typing import Optional, List
import itertools
import panel as pn
import xarray as xr
import numpy as np
from param import Parameter
from bencher.results.bench_result_base import BenchResultBase, ReduceType
from bencher.variables.results import ResultImage
from bencher.plotting.plot_filter import VarRange, PlotFilter
from bencher.utils import callable_name, listify
from bencher.video_writer import VideoWriter
from bencher.results.float_formatter import FormatFloat
from bencher.results.video_result import VideoControls
from bencher.utils import color_tuple_to_css, int_to_col
from bencher.results.composable_container.composable_container_video import ComposableContainerVideo


from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    ImageSequenceClip,
    CompositeVideoClip,
    clips_array,
    concatenate_videoclips,
)


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
            input_range=VarRange(1, 3),
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
        video_controls: VideoControls = None,
        **kwargs,
    ):
        vr = VideoWriter()

        img_array = dataset[result_var.name].to_numpy()
        if reverse:
            reversed_axes = list(reversed(range(len(img_array.shape))))
            img_array = np.transpose(img_array, reversed_axes)

        # print(img_array)

        # exit()

        # comp = ComposableContainerVideo(horizontal=False)

        # # for i in img_array:
        # comp.append(img_array[0])

        # cvc = comp.render()

        # comp2 = ComposableContainerVideo(horizontal=True)

        # comp2.append(cvc)
        # comp2.append(img_array[1])

        # cvc = comp2.render()

        # comp.append()

        # vid_array = [ImageClip(i, duration=1.0) for i in img_array]
        # cvc = clips_array([vid_array, vid_array])

        # cvc = clips_array([[cvc, cvc]])
        # cvc = clips_array([[cvc], [cvc]])
        # fn=cvc.write_videofile()

        # exit()
        # fn = img_array[0]
        # fn = vr.write_grid2d(img_array)
        cvc = self._to_video_panes_ds(dataset, self.plot_cb, 0, False, result_var,final=True, **kwargs)

        # print("CVC",cvc)
        # cvc = clips_array(cvc)
        # exit()

        print("cvc", cvc)
        print("cvctyupe", type(cvc))
        fn = vr.write_video_raw(cvc)
        print("fn", fn)

        if fn is not None:
            if video_controls is None:
                video_controls = VideoControls()
            vid = video_controls.video_container(fn, **kwargs)
            return vid
        return None

    def plot_cb(self, dataset, result_var, **kwargs):
        val = self.ds_to_container(dataset, result_var, container=None, **kwargs)
        # print(val)
        return val

    def _to_video_panes_ds(
        self,
        dataset: xr.Dataset,
        plot_callback: callable = None,
        target_dimension=0,
        horizontal=False,
        result_var=None,
        final=False,
        **kwargs,
    ) -> pn.panel:
        # todo, when dealing with time and repeats, add feature to allow custom order of dimension recursion
        ##todo remove recursion
        num_dims = len(dataset.sizes)
        dims = list(d for d in dataset.sizes)

        print("")

        print("ENTERING")
        # print(dataset)
        print("target", target_dimension)
        print("numdims", num_dims)
        print(f"dims {dims}")

        if num_dims > (target_dimension) and num_dims != 0:
            selected_dim = dims[-1]
            print(f"selected dim {selected_dim}")
            dim_color = color_tuple_to_css(int_to_col(num_dims - 2, 0.05, 1.0))

            outer_container = ComposableContainerVideo(
                name=" vs ".join(dims),
                # background_col=dim_color,
                horizontal=horizontal,
            )
            max_len = 0
            for i in range(dataset.sizes[selected_dim]):
                sliced = dataset.isel({selected_dim: i})
                label_val = sliced.coords[selected_dim].values.item()
                inner_container = ComposableContainerVideo(
                    outer_container.name,
                    # width=num_dims - target_dimension,
                    # var_name=selected_dim,
                    # var_value=label_val,
                    horizontal=horizontal,
                )
                panes = self._to_video_panes_ds(
                    sliced,
                    plot_callback=plot_callback,
                    target_dimension=target_dimension,
                    horizontal=len(sliced.sizes) <= target_dimension + 1,
                    result_var=result_var,
                )

                print(f"print append inner type {type(panes)}")
                inner_container.append(panes)

                # if inner_container.label_len > max_len:
                # max_len = inner_container.label_len

                rendered = inner_container.render()
                print(f"print append outer type {type(rendered)}")

                outer_container.append(rendered)

        else:
            print("plot callback")
            return plot_callback(dataset=dataset, result_var=result_var, **kwargs)
        print("final render")
        return outer_container.render(concatenate=final)
