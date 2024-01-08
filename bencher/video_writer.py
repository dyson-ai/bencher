from bencher import gen_video_path, gen_image_path
from PIL import Image
import numpy as np


class VideoWriter:
    def __init__(self, filename: str) -> None:
        self.images = []
        self.filename = gen_video_path(filename)

    def append(self, img):
        self.images.append(img)

    def write(self, bitrate: int = 1500) -> str:
        import moviepy.video.io.ImageSequenceClip

        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(self.images, fps=30)
        clip.write_videofile(self.filename, bitrate=f"{bitrate}k", logger=None)
        return self.filename


def add_image(np_array: np.ndarray, name: str = "img"):
    filename = gen_image_path(name)
    Image.fromarray(np_array).save(filename)
    return filename
