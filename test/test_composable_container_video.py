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
            vid.append("bad.badextension")

    def test_simple_image_length(self):

        ccv = bch.ComposableContainerVideo()
        ccv.append(self.small_img())
        ccv.append(self.small_img())

        res = ccv.render()
        self.assertEqual(res.duration, 2.0)  # limited by maximum frame time

        ccv = bch.ComposableContainerVideo()
        for _ in range(20):
            ccv.append(self.small_img())

        self.assertEqual(ccv.render().duration, 10.0)  # limited by target video duration

        ccv = bch.ComposableContainerVideo()
        for _ in range(200):
            ccv.append(self.small_img())

        # still limited by target video duration
        self.assertAlmostEqual(ccv.render().duration, 10.0)

    def test_composite_image_length(self):

        ccv = bch.ComposableContainerVideo()

        for _ in range(2):
            sub_img = bch.ComposableContainerVideo()
            sub_img.append(self.small_img())
            sub_img.append(self.small_img())
            sub_img.append(self.small_img())
            ccv.append(sub_img.render(compose_method=bch.ComposeType.right))

        # should be 2 because there are two sequential frames
        self.assertEqual(ccv.render().duration, 2.0)

        ccv = bch.ComposableContainerVideo()

        for _ in range(20):
            sub_img = bch.ComposableContainerVideo()
            sub_img.append(self.small_img())
            sub_img.append(self.small_img())
            sub_img.append(self.small_img())
            ccv.append(sub_img.render(compose_method=bch.ComposeType.right))

        # should be 10 because of the default target length
        self.assertEqual(ccv.render().duration, 10.0)

    def test_video_lengths(self):

        ccv = bch.ComposableContainerVideo()
        ccv.append(self.small_video())
        ccv.append(self.small_video())

        res = ccv.render()
        self.assertEqual(res.duration, 4.0)  # no frame limits, just concat videos

        ccv = bch.ComposableContainerVideo()
        for _ in range(20):
            ccv.append(self.small_video())

        self.assertEqual(ccv.render().duration, 40.0)  # concatted vid time

        ccv = bch.ComposableContainerVideo()
        for _ in range(200):
            ccv.append(self.small_video())

        # still concatted vid time
        self.assertAlmostEqual(ccv.render().duration, 400.0)


if __name__ == "__main__":
    unittest.main()
