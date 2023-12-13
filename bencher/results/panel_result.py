from bencher.results.bench_result_base import BenchResultBase

import panel as pn
import xarray as xr
from collections.abc import Iterable
from bencher.utils import int_to_col, color_tuple_to_css


class PanelResult(BenchResultBase):
    def to_video(self):
        vid_p = []

        def create_video(vid):  # pragma: no cover
            vid = pn.pane.Video(vid, autoplay=True)
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

    def to_image(self, container=pn.pane.PNG):
        return self.to_panes(container=container)

    def to_panes(self, container=pn.pane.panel):
        print(self.bench_cfg.result_vars)
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
