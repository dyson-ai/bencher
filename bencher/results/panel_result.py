from bencher.results.bench_result_base import BenchResultBase

import panel as pn
import xarray as xr
from collections.abc import Iterable
from bencher.utils import int_to_col, color_tuple_to_css


# from bencher.results.DividerVertical import DividerVertical

# class DividerV(Reactive):
#     """
#     A `Divider` draws a horizontal rule (a `<hr>` tag in HTML) to separate
#     multiple components in a layout. It automatically spans the full width of
#     the container.

#     Reference: https://panel.holoviz.org/reference/layouts/Divider.html

#     :Example:

#     >>> pn.Column(
#     ...     '# Lorem Ipsum',
#     ...     pn.layout.Divider(),
#     ...     'A very long text... '
#     >>> )
#     """

#     width_policy = param.ObjectSelector(default="fit", readonly=True)

#     _bokeh_model = BkDiv

#     _stylesheets: ClassVar[List[str]] = [f"{CDN_DIST}css/divider.css"]

#     def _get_model(self, doc, root=None, parent=None, comm=None):
#         properties = self._process_param_change(self._init_params())
#         model = self._bokeh_model(text="<hr>", **properties)
#         if root is None:
#             root = model
#         self._models[root.ref["id"]] = (model, parent)
#         return model


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

        outer_container = pn.Column(buttons, row)

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

        return outer_container

    def to_image(self, container=pn.pane.PNG):
        return self.to_panes(container=container)

    def to_panes(self, container=pn.pane.panel):
        var = self.bench_cfg.result_vars[0].name

        xr_dataarray = self.xr_dataset[var]
        xr_dataarray = xr_dataarray.squeeze()
        if not isinstance(xr_dataarray["repeat"].values, Iterable):
            xr_dataarray = xr_dataarray.drop_indexes("repeat")

        panes = self._to_panes(xr_dataarray, len(xr_dataarray.dims) == 1, container=container)
        return panes

    def _to_panes(
        self,
        da: xr.DataArray,
        last_item=False,
        container=pn.pane.panel,
        in_card=True,
        as_column=True,
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
                    as_column=True,
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
                    col.append(container(val))
                    col.append(pn.pane.Markdown(f"{da.dims[0]}={label}", align=align))
                    # styles={"border-top": "1px solid grey"},sizing_mode="stretch_width"
                    inner.append(col)
            else:
                for val in da.values:
                    inner.append(container(val))
            outer_container.append(inner)

        return outer_container

    

    def get_var(self, da):
        coords = list(da.coords)
        var = coords[0]
        return var

    def add_labels(self, xr_dataarray: xr.DataArray, grid_stack, row_dim_id, row=True):
        if row:
            grid_index = grid_stack.nrows
            align = ("start", "center")

        else:
            grid_index = grid_stack.ncols
            align = ("center", "start")

        row_dim_name = xr_dataarray.dims[row_dim_id]
        row_labels = xr_dataarray.coords[row_dim_name]
        for i, r in enumerate(row_labels):
            if row:
                idx = (i, grid_index)
            else:
                idx = (grid_index, i)
            # container.append( pn.pane.Markdown(f"{r.long_name}= {r.values}", align="center"))
            # container.append( pn.layout.Spacer())
            grid_stack[idx] = pn.pane.Markdown(
                f"{r.long_name}={r.values}[{r.units}]", align=align, margin=0
            )
            # grid_stack[idx].height=1

        return grid_stack

    # def display_recursive(self,xr_data_array):

    def to_image_old(self, var="img"):
        from collections.abc import Iterable

        xr_dataarray = self.xr_dataset[var]
        xr_dataarray = xr_dataarray.squeeze()
        # print(xr_dataarray["radius"].values)
        if not isinstance(xr_dataarray["repeat"].values, Iterable):
            xr_dataarray = xr_dataarray.drop_indexes("repeat")
        print("coords", xr_dataarray.coords)
        # grid_stack = pn.GridSpec(width=1500,sizing_mode="scale_both")
        # grid_stack = pn.GridSpec(sizing_mode="scale_both")
        grid_stack = pn.GridSpec()

        print("sz,mode", grid_stack.sizing_mode)
        # grid_stack = pn.GridSpec()

        # container = pn.Row()
        print(xr_dataarray.values)
        import numpy as np

        # for x in np.nditer(xr_dataarray.values)
        for idx, x in np.ndenumerate(xr_dataarray.values):
            img = pn.pane.PNG(x, align="center")
            # md = pn.pane.Markdown(f"## {v.name} = {v.values}", align="center")
            # grid_stack[idx] = pn.Column(md, img)
            # print(idx, x)
            index = (idx[0] + 1, idx[1] + 1)
            index = idx
            # grid_stack[index] = pn.Column(img,height_policy="fit",width_policy="fit")
            grid_stack[index] = img

        self.add_labels(xr_dataarray, grid_stack, 0, row=True)
        self.add_labels(xr_dataarray, grid_stack, 1, row=False)

        # grid_stack[2]

        # rows = grid_stack.nrows
        # cols = grid_stack.ncols
        # row_dim_id = 0
        # row_dim_name = xr_dataarray.dims[row_dim_id]
        # row_labels = xr_dataarray.coords[row_dim_name]
        # for i, r in enumerate(row_labels):
        #     grid_stack[i, cols] = pn.Row(
        #         pn.pane.Markdown(f"{r.long_name}= {r.values}", align="center"), pn.layout.HSpacer()
        #     )

        # print(xr_dataarray.dims)
        # print(xr_dataarray.coords["sides"])

        # grid_stack[1, 0] = pn.pane.Markdown("ax1", align="end", width=30)
        # grid_stack[2, 0] = pn.pane.Markdown("ax2", align="end", width=30)
        # from holoviews import opts

        # grid_stack.opts(opts.GridSpec(width_ratios=[1, 0.5]))
        # grid_sti

        # exit()
        print(grid_stack.grid)
        for v, v1 in zip(xr_dataarray.coords[self.get_var(xr_dataarray)], xr_dataarray.values):
            # print(v,v1)
            # print("v",v)
            # print()
            # print(v.values)
            # print("v1",v1)

            # print(v.values)
            img = pn.pane.PNG(v1[0], align="center")
            md = pn.pane.Markdown(f"## {v.name} = {v.values}", align="center")
            # container.append(pn.Column(md, img))
        # return container

        # gs2 = pn.GridSpec()
        # gs2[0,0] = grid_stack[0,0]
        # gs2[1,0] = grid_stack[1,0]

        return grid_stack
