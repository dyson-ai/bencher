import numpy as np
import moviepy.video.io.ImageSequenceClip
from pathlib import Path
from .utils import gen_video_path, gen_image_path

import moviepy
from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    ImageSequenceClip,
    clips_array,
    concatenate_videoclips,
)
from PIL import Image, ImageDraw


class VideoWriter:
    def __init__(self, filename: str = "vid") -> None:
        self.images = []
        self.image_files = []
        self.video_files = []
        self.filename = gen_video_path(filename)

    def append(self, img):
        self.images.append(img)

    def write(self) -> str:
        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(
            self.images, fps=30, with_mask=False, load_images=True
        )
        self.write_video_raw(clip)
        return self.filename

    @staticmethod
    def create_label(label, width=None, height=20):
        if width is None:
            width = len(label) * 8
        new_img = Image.new("RGB", (width, height), (255, 255, 255))
        # ImageDraw.Draw(new_img).text((width/2, 0), label, (0, 0, 0),align="center",achor="ms")
        ImageDraw.Draw(new_img).text((width / 2.0, 0), label, (0, 0, 0), anchor="mt", font_size=12)

        return new_img

    @staticmethod
    def label_image(path: Path, label, padding=20) -> Path:
        image = Image.open(path)
        new_img = VideoWriter.create_label(label, image.size[0], image.size[1] + padding)
        new_img.paste(image, (0, padding))
        return new_img

    def append_file(self, filepath, label=None):
        if label is not None:
            path = Path(filepath)
            new_path = path.with_name(path.stem + "_labelled" + path.suffix).as_posix()
            padding = 20
            match path.suffix:
                case ".png" | ".jpg":
                    image = Image.open(filepath)
                    new_img = self.create_label(label, image.size[0], image.size[1] + padding)
                    new_img.paste(image, (0, padding))
                    new_img.save(new_path)
                    self.image_files.append(new_path)
                case ".webm":
                    import warnings

                    video_clip = VideoFileClip(filepath)
                    new_img = self.create_label(label, video_clip.w, padding)

                    # Convert PIL image to MoviePy clip
                    label_clip = ImageClip(np.array(new_img), duration=video_clip.duration)

                    labeled_video_clip = clips_array([[label_clip], [video_clip]])

                    # otherwise ffmpeg complains that the file is not getting read. We don't need the file just the size
                    with warnings.catch_warnings():
                        warnings.simplefilter(action="ignore")
                        labeled_video_clip.write_videofile(new_path, remove_temp=True, logger=None)
                    self.video_files.append(new_path)
        else:
            self.image_files.append(filepath)

    def to_images_sequence(self, images, target_duration: float = 10.0, frame_time=None):
        if isinstance(images, list) and len(images) > 0:
            if frame_time is None:
                fps = len(images) / target_duration
                fps = max(fps, 1)  # never slower that 1 seconds per frame
                fps = min(fps, 30)
            else:
                fps = 1.0 / frame_time
            return ImageSequenceClip(images, fps=fps, with_mask=False)
        return None

    def write_png(self):
        clip = None
        if len(self.image_files) > 0:
            clip = self.to_images_sequence(self.image_files)
        if len(self.video_files) > 0:
            clip = concatenate_videoclips([VideoFileClip(f) for f in self.video_files])
        if clip is not None:
            clip.write_videofile(self.filename)
            return self.filename
        return None

    def write_video_raw(self, video_clip: moviepy.video.VideoClip, fps: int = 30) -> str:
        video_clip.write_videofile(
            self.filename,
            codec="libvpx",
            audio=False,
            bitrate="0",
            fps=fps,
            ffmpeg_params=["-crf", "34"],
        )
        video_clip.close()
        return self.filename


def add_image(np_array: np.ndarray, name: str = "img"):
    filename = gen_image_path(name)
    Image.fromarray(np_array).save(filename)
    return filename
