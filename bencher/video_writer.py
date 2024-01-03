import moviepy.video.io.ImageSequenceClip


class VideoWriter:
    def __init__(self, gui) -> None:
        self.images = []
        self.gui = gui

    def append(self, img):
        self.images.append(img)

    def update_gui(self, pixels):
        self.gui.set_image(pixels)
        self.append(self.gui.get_image() * 255)
        self.gui.show()

    def write(self, file, bitrate=1500):
        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(self.images, fps=30)
        # clip = clip.add_mask().rotate(90)
        clip.write_videofile(file, bitrate=f"{bitrate}k")
