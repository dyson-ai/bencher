import unittest
from bencher.video_writer import VideoWriter, add_image
import numpy as np
from pathlib import Path


class TestVideoWriter(unittest.TestCase):
    def test_converter(self):
        filename = "cachedir/vid/vid/test_vid.mp4"
        vw = VideoWriter()
        vw.filename = filename
        img = add_image(np.zeros([100, 200, 3], dtype=np.uint8), "img.png")
        img2 = add_image(np.zeros([100, 200, 3], dtype=np.uint8), "img2.png")
        vw.append(img)
        vw.append(img2)
        filename = vw.write()

        print(filename)
        converted = VideoWriter.convert_to_compatible_format(filename)
        print(converted)

        orig = Path(filename)
        conv = Path(converted)

        assert conv.name == "test_vid_fixed.mp4"
        # assert orig.absolute() ==""
        # assert conv.absolute() == ""

