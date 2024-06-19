import bencher as bch
import numpy as np
import math
import matplotlib.pyplot as plt


def polygon_points(radius: float, sides: int, start_angle: float):
    points = []
    for ang in np.linspace(0, 360, sides + 1):
        angle = math.radians(start_angle + ang)
        points.append(([math.sin(angle) * radius, math.cos(angle) * radius]))
    return points


class BenchPolygons(bch.ParametrizedSweep):
    sides = bch.IntSweep(default=3, bounds=(3, 7))
    radius = bch.FloatSweep(default=1, bounds=(0.2, 1))
    linewidth = bch.FloatSweep(default=1, bounds=(1, 10))
    linestyle = bch.StringSweep(["solid", "dashed", "dotted"])
    color = bch.StringSweep(["red", "green", "blue"])
    start_angle = bch.FloatSweep(default=0, bounds=[0, 360])
    polygon = bch.ResultImage()
    polygon_small = bch.ResultImage()

    area = bch.ResultVar()
    side_length = bch.ResultVar()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        points = polygon_points(self.radius, self.sides, self.start_angle)
        # self.hmap = hv.Curve(points)
        self.polygon = self.points_to_polygon_png(points, bch.gen_image_path("polygon"), dpi=30)
        self.polygon_small = self.points_to_polygon_png(
            points, bch.gen_image_path("polygon"), dpi=10
        )

        self.side_length = 2 * self.radius * math.sin(math.pi / self.sides)
        self.area = (self.sides * self.side_length**2) / (4 * math.tan(math.pi / self.sides))
        return super().__call__()

    def points_to_polygon_png(self, points: list[float], filename: str, dpi):
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
        fig.savefig(filename, dpi=dpi)

        return filename


def example_image_vid_sequential1(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:
    bench = BenchPolygons().to_bench(run_cfg, report)
    res = bench.plot_sweep(input_vars=["sides"])

    bench.report.append(res.to_panes(zip_results=True))

    return bench


if __name__ == "__main__":

    ex_run_cfg = bch.BenchRunCfg()
    ex_run_cfg.use_sample_cache = True
    ex_run_cfg.overwrite_sample_cache = True
    ex_run_cfg.level = 3

    example_image_vid_sequential1(ex_run_cfg).report.show()
