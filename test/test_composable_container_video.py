import unittest
import bencher as bch
import numpy as np
from bencher.example.meta.example_meta import BenchableObject
from bencher.results.composable_container import composable_container_video


class TestComposableContainerVideo(unittest.TestCase):

    def small_img(self):
        return np.array(
            [[[1, 1, 1]], [[0, 0, 0]]]
        )  # represents an image of 1x2 (keep it small for speed)

    def small_video(self, num_frames: int = 2, render_args=None):
        img = self.small_img()
        vid = bch.ComposableContainerVideo()
        for i in range(num_frames):
            vid.append(img)
        return vid.to_video(render_args)

    def test_img_seq(self):
        img = self.small_img()
        vid = bch.ComposableContainerVideo()
        vid.append(img)

        res = vid.render(bch.RenderCfg(target_duration=0.1, compose_method=bch.ComposeType.right))
        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 0.1)

        res = vid.render(bch.RenderCfg(target_duration=0.1, compose_method=bch.ComposeType.down))
        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 0.1)

        res = vid.render(
            bch.RenderCfg(target_duration=0.1, compose_method=bch.ComposeType.sequence)
        )
        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 0.1)

        # ADD A SECOND FRAME

        vid.append(img)
        res = vid.render(bch.RenderCfg(target_duration=0.1, compose_method=bch.ComposeType.right))
        self.assertEqual(res.size, (2, 2))
        self.assertEqual(res.duration, 0.1)

        res = vid.render(bch.RenderCfg(target_duration=0.1, compose_method=bch.ComposeType.down))
        self.assertEqual(res.size, (1, 4))
        self.assertEqual(res.duration, 0.1)

        res = vid.render(
            bch.RenderCfg(target_duration=0.1, compose_method=bch.ComposeType.sequence)
        )
        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 0.1)

        res = vid.render(
            bch.RenderCfg(target_duration=0.1, compose_method=bch.ComposeType.sequence)
        )
        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 0.1)  # two frames

    def test_video_seq(self):

        img = self.small_img()
        vid1 = bch.ComposableContainerVideo()
        vid1.append(img)
        vid1.append(img)

        res = vid1.render(
            bch.RenderCfg(target_duration=0.1, compose_method=bch.ComposeType.sequence)
        )

        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 0.1)  # two frames

        res = vid1.render(
            bch.RenderCfg(
                target_duration=None,
                min_frame_duration=1.0 / 30,
                max_frame_duration=1.0,
                compose_method=bch.ComposeType.sequence,
            )
        )

        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 0.1)  # two frames


if __name__ == "__main__":
    unittest.main()
