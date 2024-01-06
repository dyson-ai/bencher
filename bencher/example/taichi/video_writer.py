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

    def wiggle_camera(self, scale=1, callback=None):
        # return self.rotate_camera_circular_motion([0,0,0],0.3,100,5)
        # self.camera.yaw
        import math

        dist = self.dist
        yaw = self.yaw
        pitch = self.pitch
        target = self.target

        for y in np.arange(0, 6.28, 0.1):
            self.set_camera(
                distance=dist,
                yaw=yaw + math.sin(y) * scale,
                pitch=pitch + math.cos(y) * scale,
                target=target,
            )
            if callback is not None:
                callback()
            self.step_simulation()
