from bencher import gen_video_path

class VideoWriter:
    def __init__(self ) -> None:
        self.images = []

    def append(self, img):
        self.images.append(img)

    def write(self, file, bitrate:int=1500)->str:
        import moviepy.video.io.ImageSequenceClip
        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(self.images, fps=30)
        fn = gen_video_path(file)
        clip.write_videofile(fn, bitrate=f"{bitrate}k")
        return fn

    