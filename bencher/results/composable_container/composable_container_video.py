from __future__ import annotations
import numpy as np
from pathlib import Path
from dataclasses import dataclass
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


@dataclass(kw_only=True)
class RenderCfg:

    var_name: str = None
    var_value: str = None
    background_col: tuple[3] = (255, 255, 255)
    compose_method: ComposeType = ComposeType.sequence
    target_duration: float = 10.0
    min_frame_duration: float = 1.0 / 30
    max_frame_duration: float = 1.0


@dataclass
class ComposableContainerVideo(ComposableContainerBase):

    # render_args: RenderCfg = None

    def append(self, obj: VideoClip | ImageClip | str | np.ndarray) -> None:
        """Appends an image or video to the container

        Args:
            obj (VideoClip | ImageClip | str | np.ndarray): Any representation of an image or video

        Raises:
            RuntimeWarning: if file format is not recognised
        """

        # print(f"append obj:  {isinstance(obj, VideoClip)} {type(obj)}, {obj}")
        if isinstance(obj, VideoClip):
            self.container.append(obj)
        elif isinstance(obj, ComposableContainerVideo):
            self.container.append(obj.render())
        elif isinstance(obj, np.ndarray):
            self.container.append(ImageClip(obj))
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

    def render(self, render_cfg: RenderCfg = None) -> CompositeVideoClip:
        """Composes the images/videos into a single image/video based on the type of compose method

        Args:
            compose_method (ComposeType, optional): optionally override the default compose type. Defaults to None.

        Returns:
            CompositeVideoClip: A composite video clip containing the images/videos added via append()
        """
        if render_cfg is None:
            render_cfg = RenderCfg()

        # duration = 10.0 if render_cfg.target_duration is None else render_cfg.target_duration
            

        fps = float(len(self.container)) / render_cfg.target_duration  #
        if render_cfg.min_frame_duration is not None:
            fps = max(fps, render_cfg.min_frame_duration)  # never slower that 1 seconds per frame
        if render_cfg.max_frame_duration is not None:
            fps = min(fps, render_cfg.max_frame_duration)

        # duration = fps * len(render_args.container)
        duration = render_cfg.target_duration

        out = None
        print(f"using compose type{render_cfg.compose_method}")
        match render_cfg.compose_method:
            case ComposeType.right:
                out = clips_array([self.container], bg_color=render_cfg.background_col)
                out.duration = duration
            case ComposeType.down:
                out = clips_array([[c] for c in self.container], bg_color=render_cfg.background_col)
                out.duration = duration
            case ComposeType.sequence:
                for i in range(len(self.container)):
                    self.container[i].duration = duration / float(len(self.container))
                out = concatenate_videoclips(
                    self.container, bg_color=render_cfg.background_col, method="compose"
                )
            # case ComposeType.overlay:
            #     for i in range(len(self.container)):
            #         self.container[i].alpha = 1./len(self.container)
            #     out = CompositeVideoClip(self.container, bg_color=render_args.background_col)
            #     out.duration = fps
            case _:
                raise RuntimeError("This compose type is not supported4")

        label = self.label_formatter(render_cfg.var_name, render_cfg.var_value)
        if label is not None:
            label_len = len(label)

            print("adding label")
            label = ImageClip(np.array(VideoWriter.create_label(label)))
            label_compose = ComposeType.down
            if render_cfg.compose_method == ComposeType.down:
                label_compose = ComposeType.right
            con2 = ComposableContainerVideo()
            con2.append(label)
            con2.append(out)
            return con2.render(
                RenderCfg(
                    background_col=render_cfg.background_col,
                    compose_method=label_compose,
                    target_duration=out.duration,
                )
            )
        return out

    def to_video(self, render_args: RenderCfg = None) -> str:
        """Returns the composite video clip as a webm file path

        Returns:
            str: webm filepath
        """
        return VideoWriter().write_video_raw(self.render(render_args))
