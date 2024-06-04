import numpy as np
import moviepy.video.io.ImageSequenceClip
from pathlib import Path
from .utils import gen_video_path, gen_image_path

import moviepy
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
        if len(self.images) > 0:
            clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(
                self.images, fps=30, with_mask=False, load_images=True
            )
            self.write_video_raw(clip)
        return self.filename

    @staticmethod
    def create_label(label, width=None, height=16, color=(255, 255, 255)):
        if width is None:
            width = len(label) * 10
        new_img = Image.new("RGB", (width, height), color=color)
        # ImageDraw.Draw(new_img).text((width/2, 0), label, (0, 0, 0),align="center",achor="ms")
        ImageDraw.Draw(new_img).text(
            (width / 2.0, 0), label, (0, 0, 0), anchor="mt", font_size=height
        )

        return new_img

    @staticmethod
    def label_image(path: Path, label, padding=20, color=(255, 255, 255)) -> Path:
        image = Image.open(path)
        new_img = VideoWriter.create_label(
            label, image.size[0], image.size[1] + padding, color=color
        )
        new_img.paste(image, (0, padding))
        return new_img

    def write_video_raw(self, video_clip: moviepy.video.VideoClip, fps: int = 30) -> str:
        video_clip.write_videofile(
            self.filename,
            codec="libx264",
            audio=False,
            bitrate="0",
            fps=fps,
            ffmpeg_params=["-crf", "23"],
            threads=8,
        )
        video_clip.close()
        return self.filename


def add_image(np_array: np.ndarray, name: str = "img") -> str:
    """Creates a file on disk from a numpy array and returns the created image path"""
    filename = gen_image_path(name)
    Image.fromarray(np_array).save(filename)
    return filename
