from bencher import gen_video_path, gen_image_path
from PIL import Image
import numpy as np


class VideoWriter:
    def __init__(self, filename: str = "vid") -> None:
        self.images = []
        self.filename = gen_video_path(filename)

    def append(self, img):
        self.images.append(img)

    def write(self, bitrate: int = 1500) -> str:
        import moviepy.video.io.ImageSequenceClip

        # todo
        # if len(self.images[0.shape) == 2:
        #     for i in range(len(self.images)):
        #         self.images[i] = np.expand_dims(self.images[i], 2)

        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(self.images, fps=30)
        clip.write_videofile(self.filename, bitrate=f"{bitrate}k", logger=None)
        return self.filename


def add_image(np_array: np.ndarray, name: str = "img"):
    filename = gen_image_path(name)
    Image.fromarray(np_array).save(filename)
    return filename
