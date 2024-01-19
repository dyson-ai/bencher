from PIL import Image, ImageDraw
import numpy as np
import moviepy.video.io.ImageSequenceClip
from pathlib import Path
from .utils import gen_video_path, gen_image_path


class VideoWriter:
    def __init__(self, filename: str = "vid") -> None:
        self.images = []
        self.pngs = []
        self.filename = gen_video_path(filename)

    def append(self, img):
        self.images.append(img)

    def write(self, bitrate: int = 1500) -> str:
        # todo
        # if len(self.images[0.shape) == 2:
        #     for i in range(len(self.images)):
        #         self.images[i] = np.expand_dims(self.images[i], 2)

        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(
            self.images, fps=30, with_mask=False, load_images=True
        )
        clip.write_videofile(self.filename, bitrate=f"{bitrate}k", logger=None)
        return self.filename

    def append_png(self, png, label=None):
        if label is not None:
            image = Image.open(png)
            padding = 20
            new_img = Image.new("RGB", (image.size[0], image.size[1] + padding), (255, 255, 255))
            new_img.paste(image, (0, padding))
            ImageDraw.Draw(new_img).text((0, 0), label, (0, 0, 0))
            path = Path(png)
            new_path = path.with_name(path.stem + "_labelled" + path.suffix)
            new_img.save(new_path)
            self.pngs.append(new_path.as_posix())
        else:
            self.pngs.append(png)

    def write_png(self, bitrate: int = 1500):
        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(
            self.pngs, fps=30, with_mask=False
        )
        clip.write_videofile(self.filename, bitrate=f"{bitrate}k", fps=30, logger=None)


def add_image(np_array: np.ndarray, name: str = "img"):
    filename = gen_image_path(name)
    Image.fromarray(np_array).save(filename)
    return filename
