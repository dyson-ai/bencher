import unittest
import bencher as bch
import numpy as np


class TestComposableContainerVideo(unittest.TestCase):

    def small_img(self, size=None):
        if size is None:
            size = (2, 1)
        return np.ones((size[0], size[1], 3))
        # return np.array(
        #     [[[1, 1, 1]], [[0, 0, 0]]]
        # )  # represents an image of 1x2 (keep it small for speed)

    def small_video(self, num_frames: int = 2, render_cfg=None, size=None):
        img = self.small_img(size=size)
        vid = bch.ComposableContainerVideo()
        for _ in range(num_frames):
            vid.append(img)
        return vid.render(render_cfg)

    def test_img_seq(self):
        img = self.small_img()
        vid = bch.ComposableContainerVideo()
        vid.append(img)

        res = vid.render(bch.RenderCfg(duration=0.1, compose_method=bch.ComposeType.right))
        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 0.1)

        res = vid.deep().render(bch.RenderCfg(duration=0.1, compose_method=bch.ComposeType.down))
        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 0.1)

        res = vid.deep().render(
            bch.RenderCfg(duration=0.1, compose_method=bch.ComposeType.sequence)
        )
        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 0.1)

        # ADD A SECOND FRAME

        vid.append(img)
        res = vid.deep().render(bch.RenderCfg(duration=0.1, compose_method=bch.ComposeType.right))
        self.assertEqual(res.size, (2, 2))
        self.assertEqual(res.duration, 0.1)

        res = vid.deep().render(bch.RenderCfg(duration=0.1, compose_method=bch.ComposeType.down))
        self.assertEqual(res.size, (1, 4))
        self.assertEqual(res.duration, 0.1)

        res = vid.deep().render(
            bch.RenderCfg(duration=0.1, compose_method=bch.ComposeType.sequence)
        )
        self.assertEqual(res.size, (1, 2))
        # self.assertEqual(res.duration, 0.1)

    def test_video_seq(self):

        img = self.small_img()
        vid1 = bch.ComposableContainerVideo()
        vid1.append(img)
        vid1.append(img)

        res = vid1.deep().render(
            bch.RenderCfg(duration=0.1, compose_method=bch.ComposeType.sequence)
        )

        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 0.1)  # two frames

        render_cfg = bch.RenderCfg(
            duration=10.0,
            duration_target=True,
            min_frame_duration=1.0 / 30,
            max_frame_duration=1.0,
        )

        res = vid1.deep().render(render_cfg)

        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 2.0)  # 2 frames of minimum frame time 1.0

        vid1.append(img)

        res = vid1.render(render_cfg)
        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 3.0)  # 3 frames of minimum frame time 1.0

    def test_concat_equal_video_len(self):
        render_cfg = bch.RenderCfg(duration_target=True)
        res1 = self.small_video(num_frames=2, render_cfg=render_cfg)
        self.assertEqual(res1.size, (1, 2))
        self.assertEqual(res1.duration, 2.0)  # 3 frames of minimum frame time 1.0

        vid = bch.ComposableContainerVideo()

        vid.append(res1)
        vid.append(res1)

        res = vid.deep().render(bch.RenderCfg(bch.ComposeType.right))
        self.assertEqual(res.size, (2, 2))
        self.assertEqual(res.duration, 2.0)  # the duration of the longer clip

        res = vid.deep().render(bch.RenderCfg(bch.ComposeType.down))
        self.assertEqual(res.size, (1, 4))
        self.assertEqual(res.duration, 2.0)  # the duration of the longer clip

        res = vid.deep().render(bch.RenderCfg(bch.ComposeType.sequence))
        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 4.0)  # the duration of both clips

    def test_concat_unequal_video_len(self):
        render_cfg = bch.RenderCfg(duration_target=True)
        res1 = self.small_video(num_frames=2, render_cfg=render_cfg)
        self.assertEqual(res1.size, (1, 2))
        self.assertEqual(res1.duration, 2.0)  # 3 frames of minimum frame time 1.0

        res2 = self.small_video(num_frames=3, render_cfg=render_cfg)
        self.assertEqual(res2.size, (1, 2))
        self.assertEqual(res2.duration, 3.0)  # 3 frames of minimum frame time 1.0

        vid = bch.ComposableContainerVideo()

        vid.append(res1)
        vid.append(res2)

        res = vid.deep().render(bch.RenderCfg(bch.ComposeType.right))
        self.assertEqual(res.size, (2, 2))
        self.assertEqual(res.duration, 3.0)  # the duration of the longer clip

        res = vid.deep().render(bch.RenderCfg(bch.ComposeType.down))
        self.assertEqual(res.size, (1, 4))
        self.assertEqual(res.duration, 3.0)  # the duration of the longer clip

        res = vid.deep().render(bch.RenderCfg(bch.ComposeType.sequence))
        self.assertEqual(res.size, (1, 2))
        self.assertEqual(res.duration, 5.0)  # the duration of both clips

        res_label = vid.deep().render(bch.RenderCfg(bch.ComposeType.sequence))
        self.assertEqual(res.duration, res_label.duration)  # the duration of both clips

    def test_bad_filetype(self):
        vid = bch.ComposableContainerVideo()
        with self.assertRaises(RuntimeWarning):
            vid.append("bad.badextesnio")


if __name__ == "__main__":
    unittest.main()
