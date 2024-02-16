import numpy as np
from pathlib import Path
from moviepy.editor import (
    ImageClip,
    CompositeVideoClip,
    clips_array,
    concatenate_videoclips,
    VideoClip,
    VideoFileClip,
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
        compose_method: ComposeType = None,
        target_duration: float = None,
        min_frame_duration: float = None,
    ) -> None:
        super().__init__(
            compose_method=compose_method if compose_method is not None else ComposeType.sequence
        )
        self.name = name
        self.container = []
        self.background_col = background_col
        # self.background_col = None
        self.target_duration = 10.0 if target_duration is None else float(target_duration)
        self.min_frame_duration = 1.0 if min_frame_duration is None else float(min_frame_duration)
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
            path = Path(obj)
            extension = str.lower(path.suffix)
            if extension in [".jpg", ".jepg", ".png"]:
                self.container.append(ImageClip(obj))
            elif extension in [".mpeg", ".mpg", ".mp4", ".webm"]:
                print(obj)
                self.container.append(VideoFileClip(obj))
            else:
                raise RuntimeWarning(f"unsupported filetype {extension}")

            # if self.label is not None:
            # img_obj = np.array(VideoWriter.label_image(obj, self.label))
            # else:
            # img_obj = obj

    def render(self, compose_method=None) -> CompositeVideoClip:
        print(self.target_duration)
        fps = len(self.container) / self.target_duration
        fps = max(fps, self.min_frame_duration)  # never slower that 1 seconds per frame
        fps = min(fps, 30.0)
        print("fps", fps)
        if compose_method is None:
            compose_method = self.compose_method

        out = None
        print(f"using compose type{compose_method}")
        match compose_method:
            case ComposeType.right:
                out = clips_array([self.container], bg_color=self.background_col)
                out.duration = self.target_duration
            case ComposeType.down:
                out = clips_array([[c] for c in self.container], bg_color=self.background_col)
                out.duration = self.target_duration

            case ComposeType.sequence:
                # out = concatenate_videoclips(self.container,method="compose")
                # out = concatenate_videoclips(self.container,bg_color=self.background_col)

                for i in range(len(self.container)):
                    self.container[i].duration = 1.0 / fps
                out = concatenate_videoclips(
                    self.container, bg_color=self.background_col, method="compose"
                )
                # out.duration = fps * len(self.container)

            # case ComposeType.overlay:
            #     for i in range(len(self.container)):
            #         self.container[i].alpha = 1./len(self.container)
            #     out = CompositeVideoClip(self.container, bg_color=self.background_col)
            #     out.duration = fps
            case _:
                raise RuntimeError("This compose type is not supported4")

        print(out.duration)

        if self.label is not None:
            print("adding label")
            label = ImageClip(np.array(VideoWriter.create_label(self.label)))
            label_compose = ComposeType.down
            if compose_method == ComposeType.down:
                label_compose = ComposeType.right
            con2 = ComposableContainerVideo(
                background_col=self.background_col,
                compose_method=label_compose,
                target_duration=out.duration,
            )
            con2.append(label)
            con2.append(out)
            return con2.render()
        return out

    def to_video(self) -> str:
        return VideoWriter().write_video_raw(self.render())
