import numpy as np
import moviepy.video.io.ImageSequenceClip
from pathlib import Path
from .utils import gen_video_path, gen_image_path
import moviepy
from moviepy.editor import VideoFileClip, ImageClip, ImageSequenceClip
from PIL import Image, ImageDraw
from moviepy.editor import clips_array, concatenate_videoclips


class VideoWriter:
    def __init__(self, filename: str = "vid") -> None:
        self.images = []
        self.image_files = []
        self.video_files = []
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

    def create_label(self, label, width, height=20):
        new_img = Image.new("RGB", (width, height), (255, 255, 255))
        ImageDraw.Draw(new_img).text((0, 0), label, (0, 0, 0))
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

    def write_png(self, bitrate: int = 1500, target_duration: float = 10.0, frame_time=None):
        if frame_time is None:
            fps = len(self.image_files) / target_duration
            fps = max(fps, 1)  # never slower that 1 seconds per frame
            fps = min(fps, 30)
        else:
            fps = 1.0 / frame_time

        if len(self.image_files) > 0:
            clip = ImageSequenceClip(self.image_files, fps=fps, with_mask=False)
            clip.write_videofile(self.filename, bitrate=f"{bitrate}k", logger=None)
        if len(self.video_files) > 0:
            clip = concatenate_videoclips([VideoFileClip(f) for f in self.video_files])
            clip.write_videofile(self.filename, logger=None)
            # clip = ImageSequenceClip(self.image_files, fps=fps, with_mask=False)


def add_image(np_array: np.ndarray, name: str = "img"):
    filename = gen_image_path(name)
    Image.fromarray(np_array).save(filename)
    return filename
