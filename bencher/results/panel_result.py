from bencher.results.bench_result_base import BenchResultBase

import panel as pn


class PanelResult(BenchResultBase):
    # def __init__(self, xr_dataset) -> None:
    # super().__init__(xr_dataset)

    def to_video(self, var="vid"):
        # for self.bench_cfg.input_vars:

        xr_dataarray = self.xr_dataset[var]

        row = pn.Row()

        play_btn = pn.widgets.Button(name="Play Videos")
        pause_bth = pn.widgets.Button(name="Pause Videos")
        loop_btn = pn.widgets.Button(name="Loop Videos")
        reset_btn = pn.widgets.Button(name="Reset Videos")

        vid_p = []

        buttons = pn.Row(play_btn, loop_btn, pause_bth, reset_btn)

        container = pn.Column(buttons, row)

        for v, v1 in zip(xr_dataarray.coords[self.get_var(xr_dataarray)], xr_dataarray.values):
            vid = pn.pane.Video(v1[0], autoplay=True)
            vid.loop = True
            vid_p.append(vid)
            row.append(pn.Column(pn.pane.Markdown(f"## {v.name} = {v.values}"), vid))

        def play_vid(_):
            for r in vid_p:
                r.paused = False
                r.loop = False

        def pause_vid(_):
            for r in vid_p:
                r.paused = True

        def reset_vid(_):
            for r in vid_p:
                r.paused = False
                r.time = 0

        def loop_vid(_):
            for r in vid_p:
                r.paused = False
                r.time = 0
                r.loop = True

        pn.bind(play_vid, play_btn, watch=True)
        pn.bind(loop_vid, loop_btn, watch=True)
        pn.bind(pause_vid, pause_bth, watch=True)
        pn.bind(reset_vid, reset_btn, watch=True)

        return container

    # def map_to_type(self,)

    def get_var(self, da):
        coords = list(da.coords)
        var = coords[0]
        return var

    def to_image(self, var="img"):
        xr_dataarray = self.xr_dataset[var]
        container = pn.Row()
        for v, v1 in zip(xr_dataarray.coords[self.get_var(xr_dataarray)], xr_dataarray.values):
            img = pn.pane.PNG(v1[0])
            container.append(pn.Column(pn.pane.Markdown(f"## {v.name} = {v.values}"), img))
        return container


# import numpy as np
# import panel as pn


# def print_n_dimensional_array(arr):
#     def print_recursively(sub_arr, depth, index_str):
#         if isinstance(sub_arr, np.ndarray):
#             accordion = pn.Accordion(margin=(5, 0, 10, depth))
#             accordion.append(
#                 (
#                     f"{index_str}:",
#                     pn.Column(
#                         *[
#                             print_recursively(sub_elem, depth + 20, f"[{i}]")
#                             for i, sub_elem in enumerate(sub_arr)
#                         ]
#                     ),
#                 )
#             )
#             accordion.active=[0]

#             return accordion
#         else:
#             return pn.pane.Str(f"{' ' * depth}{index_str} = {sub_arr}")

#     return print_recursively(arr, 0, "Array Contents")


# import numpy as np
# import panel as pn
# import xarray as xr


# def print_xarray_dataarray(da):
#     def print_recursively(sub_arr, depth, index_str):
#         if isinstance(sub_arr, xr.DataArray):
#             accordion = pn.Accordion(margin=(5, 0, 10, depth))
#             for coord in sub_arr.coords:
#                 if sub_arr[coord].ndim == 0:
#                     # Handle 0-dimensional arrays
#                     accordion.append(
#                         (
#                             f"{coord}:",
#                             pn.pane.Str(f"{' ' * (depth + 20)}{coord} = {sub_arr[coord].values}"),
#                         )
#                     )
#                 else:
#                     accordion.append(
#                         (
#                             f"{coord}:",
#                             pn.Column(
#                                 *[
#                                     print_recursively(
#                                         sub_arr.loc[{coord: val}],
#                                         depth + 20,
#                                         f"{coord}={val}",
#                                     )
#                                     for val in sub_arr[coord].values
#                                 ]
#                             ),
#                         )
#                     )
#             accordion.active = list(range(len(accordion)))
#             return accordion
#         else:
#             return pn.pane.Str(f"{' ' * depth}{index_str} = {sub_arr}")

#     return print_recursively(da, 0, "DataArray Contents")


# # Example usage:
# data = np.random.rand(2, 3, 4)
# coords = {
#     "x": np.linspace(0, 1, 2),
#     "y": np.linspace(10, 20, 3),
#     "z": np.linspace(100, 110, 4),
# }
# da = xr.DataArray(data, coords=coords, dims=["x", "y", "z"])
# output = print_xarray_dataarray(da)
# pn.Column(output).show()


# exit()
