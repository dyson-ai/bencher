import unittest
from bencher.video_writer import VideoWriter 


class TestVideoWriter(unittest.TestCase):

    def test_converter(self):
        VideoWriter.convert_to_compatible_format("/home/ags/projects/bencher/cachedir/vid/vid/vid_0a53253e-a939-4cea-9cf1-ea5f1b96c5dc.mp4")
