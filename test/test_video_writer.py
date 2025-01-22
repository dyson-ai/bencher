import unittest
from bencher.video_writer import VideoWriter ,add_image
import numpy as np

class TestVideoWriter(unittest.TestCase):

    def test_converter(self):

        filename = "test_vid.mp4"
        vw=VideoWriter(filename)

        img = add_image(np.zeros([100, 200, 3], dtype=np.uint8),"img.png")
        img2 = add_image(np.zeros([100, 200, 3], dtype=np.uint8),"img2.png")
        vw.append(img)
        vw.append(img2)
        vw.write()
        converted=VideoWriter.convert_to_compatible_format(filename)

        assert converted == "test_vid_fixed.mp4"

