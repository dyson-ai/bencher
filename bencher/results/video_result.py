from typing import Optional, Any
from pathlib import Path
from functools import partial
import panel as pn
import xarray as xr
from param import Parameter
from bencher.results.bench_result_base import BenchResultBase, ReduceType
from bencher.variables.results import (
    ResultVideo,
    ResultContainer,
    ResultReference,
    PANEL_TYPES,
)


class VideoControls:
    def __init__(self) -> None:
        # pass
        self.vid_p = []

    def video_container(self, path, **kwargs):
        if path is not None and Path(path).exists():
            vid = pn.pane.Video(path, autoplay=True, **kwargs)
            vid.loop = True
            self.vid_p.append(vid)
            return vid
        return pn.pane.Markdown(f"video does not exist {path}")

    def video_controls(self, **kwargs) -> Optional[pn.Column]:
        def play_vid(_):  # pragma: no cover
            for r in self.vid_p:
                r.paused = False
                # r.loop = True

        # def pause_vid(_):  # pragma: no cover
        #     for r in self.vid_p:
        #         r.paused = True

        def reset_vid(_):  # pragma: no cover
            for r in self.vid_p:
                r.paused = False
                r.time = 0

        # def loop_vid(_):  # pragma: no cover
        #     for r in self.vid_p:
        #         r.paused = False
        #         r.time = 0
        #         r.loop = True

        button_names = ["Play Videos", "Pause Videos", "Loop Videos", "Reset Videos"]
        # buttom_cb = [play_vid, pause_vid, reset_vid, loop_vid]
        buttom_cb = [play_vid, reset_vid]

        buttons = pn.Row()

        for name, cb in zip(button_names, buttom_cb):
            button = pn.widgets.Button(name=name)
            pn.bind(cb, button, watch=True)
            buttons.append(button)

        return pn.Column(buttons)
