import numpy as np
from moviepy.editor import (
    ImageClip,
    CompositeVideoClip,
    clips_array,
    concatenate_videoclips,
    VideoClip,
)

from bencher.results.composable_container.composable_container_base import (
    ComposableContainerBase,
    ComposeType,
)
from bencher.video_writer import VideoWriter


class ComposableContainerVideo(ComposableContainerBase):
    def __init__(
        self,
        name: str = None,
        var_name: str = None,
        var_value: str = None,
        background_col: tuple[3] = (255, 255, 255),
        # horizontal: bool = True,
        compose_method: ComposeType = ComposeType.right,
    ) -> None:
        # super().__init__(horizontal)
        self.name = name
        self.container = []
        self.background_col = background_col
        # self.background_col = None
        self.target_duration = 10.0
        self.var_name = var_name
        self.compose_method = compose_method

        self.label = self.label_formatter(var_name, var_value)
        if self.label is not None:
            self.label_len = len(self.label)

        # label = self.label_formatter(var_name, var_value)
        # if label is not None:
        # self.label_len = len(label)
        # side = pn.pane.Markdown(label, align=align)
        # self.append(side)

    def append(self, obj: VideoClip | str) -> None:
        print(f"append obj:  {isinstance(obj, VideoClip)} {type(obj)}, {obj}")
        if isinstance(obj, VideoClip):
            self.container.append(obj)
        elif isinstance(obj, ComposableContainerVideo):
            self.container.append(obj.render())
        else:
            # if self.label is not None:
            # img_obj = np.array(VideoWriter.label_image(obj, self.label))
            # else:
            # img_obj = obj
            self.container.append(ImageClip(obj))

    def render(self, compose_method: ComposeType = None) -> CompositeVideoClip:
        fps = len(self.container) / self.target_duration
        fps = max(fps, 1.0)  # never slower that 1 seconds per frame
        fps = min(fps, 30.0)

        if compose_method is None:
            compose_method = self.compose_method

        for i in range(len(self.container)):
            self.container[i].duration = 1.0 / fps

        for i in range(len(self.container)):
            print(self.container[i].duration)

        out = None
        print(f"using compose type{compose_method}")
        match compose_method:
            case ComposeType.right:
                out = clips_array([self.container], bg_color=self.background_col)
                out.duration = fps * len(self.container)
                # out.duration = len
            case ComposeType.down:
                out = clips_array([[c] for c in self.container], bg_color=self.background_col)
                out.duration = fps * len(self.container)

            case ComposeType.sequence:
                # out = concatenate_videoclips(self.container,method="compose")
                # out = concatenate_videoclips(self.container,bg_color=self.background_col)
                out = concatenate_videoclips(self.container,bg_color=self.background_col,method="compose")

            case ComposeType.overlay:
                # for i in range(len(self.container)):
                # self.container[i].alpha = 0.1
                out = CompositeVideoClip(self.container)
                out.duration = fps

                # out = con
            case _:
                raise RuntimeError("This compose type is not supported4")

        # print(out.duration)
        if self.label is not None:
            print("adding label")
            label = ImageClip(np.array(VideoWriter.create_label(self.label)))
            label_compose = ComposeType.down
            if compose_method == ComposeType.down:
                label_compose = ComposeType.right
            con2 = ComposableContainerVideo(
                background_col=self.background_col, compose_method=label_compose
            )
            con2.append(label)
            con2.append(out)
            return con2.render()
        return out
