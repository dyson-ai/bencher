from bencher.results.bench_result_base import BenchResultBase

import panel as pn


class PanelResult(BenchResultBase):
    def __init__(self, xr_dataset):
        super().__init__(xr_dataset)

    def to_video(self):
        vids = self.xr_dataset["vid"]

        row = pn.Row()
        play = pn.widgets.Button(name="Play Videos")
        pause = pn.widgets.Button(name="Pause Videos")
        reset = pn.widgets.Button(name="Reset Videos")

        vid_p = []

        buttons = pn.Row(play, pause, reset)

        container = pn.Column(buttons,row)

        for v in vids.values:
            vid = pn.pane.Video(v[0], autoplay=True)
            # vid.paused=False
            # vid.autoplay=True
            vid_p.append(vid)
            row.append(vid)

        def play_vid(event):
            for r in vid_p:
                r.paused = False

        def pause_vid(event):
            for r in vid_p:
                r.paused = True

        def reset_vid(event):
            for r in vid_p:
                r.paused = False
                r.time = 0

        pn.bind(play_vid, play, watch=True)
        pn.bind(pause_vid, pause, watch=True)
        pn.bind(reset_vid, reset, watch=True)





        return container
