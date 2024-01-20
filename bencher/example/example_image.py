import bencher as bch
import numpy as np
import math
import matplotlib.pyplot as plt


def polygon_points(radius: float, sides: int):
    points = []
    for ang in np.linspace(0, math.pi * 2, sides + 1):
        points.append(([math.sin(ang) * radius, math.cos(ang) * radius]))
    return points


class BenchPolygons(bch.ParametrizedSweep):
    sides = bch.IntSweep(default=3, bounds=(3, 7))
    radius = bch.FloatSweep(default=1, bounds=(0.2, 1))
    linewidth = bch.FloatSweep(default=1, bounds=(1, 10))
    linestyle = bch.StringSweep(["solid", "dashed", "dotted"])
    color = bch.StringSweep(["red", "green", "blue"])
    polygon = bch.ResultImage()
    # hmap = bch.ResultHmap()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        points = polygon_points(self.radius, self.sides)
        # self.hmap = hv.Curve(points)
        self.polygon = self.points_to_polygon_png(points, bch.gen_image_path("polygon"))
        return super().__call__()

    def points_to_polygon_png(self, points: list[float], filename: str):
        """Draw a closed polygon and save to png"""
        fig = plt.figure(frameon=False)
        ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0], frameon=False)
        ax.set_axis_off()
        ax.plot(
            [p[0] for p in points],
            [p[1] for p in points],
            linewidth=self.linewidth,
            linestyle=self.linestyle,
            color=self.color,
        )
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)

        ax.set_aspect("equal")
        fig.add_axes(ax)
        fig.savefig(filename, dpi=50)

        return filename


def example_image(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    bench = bch.Bench("polygons", BenchPolygons(), run_cfg=run_cfg, report=report)

    for s in [
        [BenchPolygons.param.sides],
        [BenchPolygons.param.sides, BenchPolygons.param.linewidth],
        [BenchPolygons.param.sides, BenchPolygons.param.linewidth, BenchPolygons.param.linestyle],
        [
            BenchPolygons.param.sides,
            BenchPolygons.param.linewidth,
            BenchPolygons.param.linestyle,
            BenchPolygons.param.color,
        ],
        [
            BenchPolygons.param.sides,
            BenchPolygons.param.linewidth,
            BenchPolygons.param.linestyle,
            BenchPolygons.param.color,
            BenchPolygons.param.radius,
        ],
    ]:
        bench.plot_sweep(
            f"Polygons Sweeping {len(s)} Parameters",
            input_vars=s,
            result_vars=[BenchPolygons.param.polygon],
        )

    return bench


if __name__ == "__main__":

    def example_image_vid(
        run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
    ) -> bch.Bench:
        bench = BenchPolygons().to_bench(run_cfg, report)
        bench.plot_sweep(input_vars=["sides", "radius", "color"], plot=True)
        return bench

    def example_image_vid_sequential(
        run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
    ) -> bch.Bench:
        bench = BenchPolygons().to_bench(run_cfg, report)
        res_list = bench.sweep_sequential(
            input_vars=["radius", "sides", "linewidth", "color"], group_size=3
        )
        for r in res_list:
            bench.report.append(r.to_video_summary())
        return bench

    # def example_image_pairs()

    ex_run_cfg = bch.BenchRunCfg()
    ex_run_cfg.use_sample_cache = True
    # ex_run_cfg.debug = True
    # ex_run_cfg.repeats = 2
    ex_run_cfg.level = 3
    # example_image_vid(ex_run_cfg).report.show()
    example_image_vid_sequential(ex_run_cfg).report.show()
    # example_image(ex_run_cfg).report.show()
