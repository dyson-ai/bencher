import numpy as np
from moviepy.editor import (
    ImageClip,
    CompositeVideoClip,
    clips_array,
    concatenate_videoclips,
    VideoClip,
)

from bencher.results.composable_container.composable_container import ComposableContainerBase
from bencher.video_writer import VideoWriter


class ComposableContainerVideo(ComposableContainerBase):
    def __init__(
        self,
        name=None,
        var_name=None,
        var_value=None,
        background_col: tuple[3] = (255, 255, 255),
        horizontal: bool = True,
    ) -> None:
        super().__init__(horizontal)
        self.name = name
        self.container = []
        self.background_col = background_col
        # self.width = width

        self.label = self.label_formatter(var_name, var_value)
        if self.label is not None:
            self.label_len = len(self.label)

    def append(self, obj):
        if isinstance(obj, VideoClip):
            self.container.append(obj)
        else:
            if self.label is not None:
                img = VideoWriter.label_image(obj, self.label)
                self.container.append(ImageClip(np.array(img), duration=1.0))
            else:
                self.container.append(ImageClip(obj, duration=1.0))

    def render(self, concatenate=False) -> CompositeVideoClip:
        if concatenate:
            return concatenate_videoclips(self.container)
        if self.horizontal:
            # if self.label is not None:
            #     width =  self.label_len*6
            #     img = VideoWriter.create_label(self.label, width=width)
            #     side = ImageClip(np.array(img), duration=1.0)
            #     self.container.insert(0, side)
            clips = [self.container]
        else:
            clips = [[c] for c in self.container]
        return clips_array(clips, bg_color=self.background_col)
