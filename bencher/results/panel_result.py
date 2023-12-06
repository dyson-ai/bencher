from bencher.results.bench_result_base import BenchResultBase

import panel as pn


class PanelResult(BenchResultBase):
    # def __init__(self, xr_dataset) -> None:
        # super().__init__(xr_dataset)

    def to_video(self):
        xr_dataarray = self.xr_dataset["vid"]

        row = pn.Row()
        play = pn.widgets.Button(name="Play Videos")
        pause = pn.widgets.Button(name="Pause Videos")
        reset = pn.widgets.Button(name="Reset Videos")

        vid_p = []

        buttons = pn.Row(play, pause, reset)

        container = pn.Column(buttons, row)

        for v, v1 in zip(xr_dataarray.coords[self.get_var(xr_dataarray)], xr_dataarray.values):
            vid = pn.pane.Video(v1[0], autoplay=True)
            vid_p.append(vid)
            row.append(pn.Column(pn.pane.Markdown(f"## {v.name} = {v.values}"), vid))

        def play_vid():
            for r in vid_p:
                r.paused = False

        def pause_vid():
            for r in vid_p:
                r.paused = True

        def reset_vid():
            for r in vid_p:
                r.paused = False
                r.time = 0

        pn.bind(play_vid, play, watch=True)
        pn.bind(pause_vid, pause, watch=True)
        pn.bind(reset_vid, reset, watch=True)
        return container

    # def map_to_type(self,)

    def get_var(self, da):
        return da.coords[0]

    def to_image(self):
        xr_dataarray = self.xr_dataset["img"]
        container = pn.Row()
        for v, v1 in zip(xr_dataarray.coords[self.get_var(xr_dataarray)], xr_dataarray.values):
            img = pn.pane.PNG(v1[0])
            container.append(pn.Column(pn.pane.Markdown(f"## {v.name} = {v.values}"), img))
        return container
