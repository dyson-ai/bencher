import panel as pn

import moviepy
from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    ImageSequenceClip,
    CompositeVideoClip,
    clips_array,
    concatenate_videoclips,
    VideoClip,
)
from PIL import Image, ImageDraw

from bencher.results.composable_container.composable_container import ComposableContainerBase


class ComposableContainerVideo(ComposableContainerBase):
    def __init__(
        self,
        name=None,
        var_name=None,
        var_value=None,
        width=None,
        background_col: tuple[3] = (255, 255, 255),
        horizontal: bool = True,
        **kwarg,
    ) -> None:
        super().__init__(horizontal)

        self.name = name

        # self.container =

        self.container = []

        # self.container = ""
        self.background_col = background_col

        # if horizontal:
        #     self.container = pn.Column(**container_args)
        #     align = ("center", "center")
        # else:
        #     self.container = pn.Row(**container_args)
        #     align = ("end", "center")

        label = self.label_formatter(var_name, var_value)
        if label is not None:
            self.label_len = len(label)
        #     side = pn.pane.Markdown(label, align=align)
        #     self.append(side)

    def append(self, obj):
        if isinstance(obj, VideoClip):
            self.container.append(obj)
        else:
            self.container.append(ImageClip(obj, duration=1.0))

    def render(self, concatenate=False) -> CompositeVideoClip:
        if concatenate:
            return concatenate_videoclips(self.container)
        if self.horizontal:
            clips = [self.container]
        else:
            clips = [[c] for c in self.container]
        return clips_array(clips, bg_color=self.background_col)
