import bencher as bch
import numpy as np
import math
import holoviews as hv
import matplotlib.pyplot as plt


def polygon_points(radius: float, sides: int):
    points = []
    for ang in np.linspace(0, math.pi * 2, sides + 1):
        points.append(([math.sin(ang) * radius, math.cos(ang) * radius]))
    return points


class BenchPolygons(bch.ParametrizedSweep):
    sides = bch.IntSweep(default=3, bounds=(3, 5))
    radius = bch.FloatSweep(default=1, bounds=(1, 2))
    linewidth = bch.FloatSweep(default=1, bounds=(1, 10))
    linestyle = bch.StringSweep(["solid", "dashed", "dotted"])
    color = bch.StringSweep(["red", "green", "blue"])
    polygon = bch.ResultImage()
    hmap = bch.ResultHmap()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        points = polygon_points(self.radius, self.sides)
        self.hmap = hv.Curve(points)
        self.polygon = self.points_to_polygon_png(points, self.gen_image_path("polygon"))
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
        ax.set_aspect("equal")
        fig.add_axes(ax)
        fig.savefig(filename, dpi=50)
        return filename


def example_image(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    bench = bch.Bench("polygons", BenchPolygons(), run_cfg=run_cfg, report=report)

    # bench.plot_sweep("Polygons", input_vars=[BenchPolygons.param.sides])

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
        # [
        #     BenchPolygons.param.sides,
        #     BenchPolygons.param.linewidth,
        #     BenchPolygons.param.linestyle,
        #     BenchPolygons.param.color,
        #     BenchPolygons.param.radius,
        # ],
    ]:
        bench.plot_sweep("Polygons", input_vars=s, result_vars=[BenchPolygons.param.polygon])

    return bench


if __name__ == "__main__":
    example_image(bch.BenchRunCfg(level=2)).report.show()
