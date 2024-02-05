import numpy as np
from moviepy.editor import (
    ImageClip,
    CompositeVideoClip,
    clips_array,
    concatenate_videoclips,
    VideoClip,
)

from bencher.results.composable_container.composable_container_base import ComposableContainerBase
from bencher.video_writer import VideoWriter


class ComposableContainerVideo(ComposableContainerBase):
    def __init__(
        self,
        name: str = None,
        var_name: str = None,
        var_value: str = None,
        background_col: tuple[3] = (255, 255, 255),
        horizontal: bool = True,
    ) -> None:
        super().__init__(horizontal)
        self.name = name
        self.container = []
        self.background_col = background_col
        self.target_duration = 10.0
        self.var_name = var_name

        self.label = self.label_formatter(var_name, var_value)
        if self.label is not None:
            self.label_len = len(self.label)

        # label = self.label_formatter(var_name, var_value)
        # if label is not None:
        # self.label_len = len(label)
        # side = pn.pane.Markdown(label, align=align)
        # self.append(side)

    def append(self, obj: VideoClip | str) -> None:
        if isinstance(obj, VideoClip):
            self.container.append(obj)
        else:
            # if self.label is not None:
            # img_obj = np.array(VideoWriter.label_image(obj, self.label))
            # else:
            # img_obj = obj
            self.container.append(ImageClip(obj))

    def render(self, concatenate: bool = False) -> CompositeVideoClip:
        fps = len(self.container) / self.target_duration
        fps = max(fps, 1.0)  # never slower that 1 seconds per frame
        fps = min(fps, 30.0)

        for i in range(len(self.container)):
            self.container[i].duration = 1.0 / fps
        if concatenate:
            out = concatenate_videoclips(self.container)
        else:
            if self.horizontal:
                clips = [self.container]
            else:
                clips = [[c] for c in self.container]
            out = clips_array(clips, bg_color=self.background_col)

        if self.label is not None:
            label = ImageClip(np.array(VideoWriter.create_label(self.label)))
            con2 = ComposableContainerVideo(
                background_col=self.background_col,
                horizontal=not self.horizontal,
            )
            con2.append(label)
            con2.append(out)
            return con2.render()
        return out
