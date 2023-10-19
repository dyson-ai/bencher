import bencher as bch
from bencher.utils import int_to_col

import math
import holoviews as hv
from typing import Any, List
import panel as pn
from holoviews import opts


class LevelsExample(bch.ParametrizedSweep):
    xval = bch.FloatSweep(bounds=[0, 3.14])
    yval = bch.FloatSweep(bounds=[0, 3.14])
    level = bch.IntSweep(default=1, bounds=[1, 6])

    output = bch.ResultVar(units="v")
    hmap = bch.ResultHmap()

    def __call__(self, **kwargs: Any) -> Any:
        self.update_params_from_kwargs(**kwargs)
        self.output = math.sin(self.xval) + math.cos(self.yval)
        self.hmap = hv.Points((self.xval, self.yval)).opts(
            marker="o", size=110 - self.level * 20, color=int_to_col(self.level - 1)
        )

        return self.get_results_values_as_dict()


class RunWithLevel(bch.ParametrizedSweep):
    level = bch.IntSweep(default=1, bounds=[1, 8])
    dimensions = bch.IntSweep(default=1, bounds=[1, 2])

    level_samples = bch.ResultVar()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)

        self.level_samples = int(
            pow(
                len(bch.FloatSweep(bounds=[0, 1]).with_level(self.level).values(False)),
                self.dimensions,
            )
        )
        return self.get_results_values_as_dict()


def run_with_dim(bench: bch.Bench, dims: List[bch.SweepBase]):
    results = []
    for level in range(1, 6):
        print(level)
        res = bench.plot_sweep(
            f"Level:{level}",
            input_vars=dims,
            const_vars=LevelsExample.get_input_defaults(
                [LevelsExample.param.level.with_const(level)]
            ),
            result_vars=[LevelsExample.param.output, LevelsExample.param.hmap],
            run_cfg=bch.BenchRunCfg(level=level, auto_plot=False),
        )

        results.append(res)
    return results


def run_levels_1D(bench: bch.Bench) -> bch.Bench:
    results = run_with_dim(bench, [LevelsExample.param.xval])
    bench.report.append_title("Using Levels to define sample density")

    bench1 = bch.Bench("levels", RunWithLevel(), run_cfg=bch.BenchRunCfg(auto_plot=False))
    res1 = bench1.plot_sweep("Levels", input_vars=[RunWithLevel.param.level])

    bench.report.append_markdown(
        "Sample levels let you perform parameter sweeps without having to decide how many samples to take.  If you perform a sweep at level 1, then all the points are reused when sampling at level 2.  The higher levels reuse the points from lower levels to avoid having to recompute potentially expensive samples. The other advantage is that it enables a workflow where you can quickly see the results of the sweep at a low resolution to sense check the code, and then run it at a high level to get the fidelity you want.  When calling a sweep at a high level, you can publish the intermediate lower level results as the computiation continues so that you can track the progress of the computation and end the sweep early when you have sufficient resolution",
        width=600,
    )
    row = pn.Row()
    row.append(res1.to_table())
    row.append(res1.to_curve().opts(shared_axes=False))
    bench.report.append(row)

    bench.report.append_markdown(
        "Level 1 returns a single point at the lower bound of the parameter. Level 2 uses the uppper and lower bounds of the parameter. All subsequent levels are created by adding a sample between each previously calculated sample to ensure that all previous values can be reused while retaining an equal sample spacing.  The following plots show the sample points as circles and the corresponding plot of a sin function sampled at that level.",
        width=600,
    )

    combined_pts = hv.Overlay()
    combined_curve = hv.Overlay()
    for it, r in enumerate(results):
        lvl = it + 1
        row = pn.Row()
        pts = r.to_holomap().overlay().opts(title=f"Sample Points for level: {lvl}", height=300)
        crv = r.to_curve().opts(shared_axes=False, height=300) * r.to_hv_dataset().to(
            hv.Scatter
        ).opts(title=f"Function Values for level: {lvl}", size=5, height=300, shared_axes=False)

        combined_pts *= pts
        combined_curve *= crv
        row.append(pts)
        row.append(crv)
        bench.report.append_markdown(f"## {r.title}")
        bench.report.append(row)

    bench.report.append_markdown(
        "This plot overlays the previous plots into a single image. It shows how each level overlaps the previous level"
    )

    bench.report.append(pn.Row(combined_pts, combined_curve))
    return bench


def run_levels_2D(bench: bch.Bench) -> bch.Bench:
    results = run_with_dim(bench, [LevelsExample.param.xval, LevelsExample.param.yval])
    bench.report.append_markdown("# Using Levels to define 2D sample density", "Levels 2D")

    bench1 = bch.Bench("lol", RunWithLevel(), run_cfg=bch.BenchRunCfg(auto_plot=False))
    res1 = bench1.plot_sweep(
        "Levels",
        input_vars=[RunWithLevel.param.level],
        const_vars=[RunWithLevel.param.dimensions.with_const(2)],
    )
    row = pn.Row()
    row.append(res1.to_table())
    row.append(res1.to_curve().opts(shared_axes=False))
    bench.report.append(row)

    for it, r in enumerate(results):
        lvl = it + 1
        row = pn.Row()
        bench.report.append_markdown(f"## {r.title}")
        row.append(
            r.to_holomap()
            .overlay()
            .opts(title=f"Sample Points for level: {lvl}", shared_axes=False)
        )
        row.append(
            r.to_heatmap().opts(title=f"Function Value Heatmap for level: {lvl}", shared_axes=False)
        )
        bench.report.append(row)

    bench.report.append_markdown(
        "This plot overlays the previous plots into a single image. It shows how each level overlaps the previous level"
    )
    overlay = hv.Overlay()
    for lvl, r in enumerate(results):
        overlay *= (
            r.to_holomap()
            .overlay()
            .opts(width=1000, height=1000, show_legend=False, shared_axes=False)
        )

    bench.report.append(overlay)
    return bench


def run_levels(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    hv.extension("bokeh")
    opts.defaults(
        opts.Curve(show_legend=False),
        opts.Points(show_legend=False),
    )

    bench = bch.Bench("Levels", LevelsExample(), run_cfg=run_cfg, report=report)
    bench = run_levels_1D(bench)
    bench = run_levels_2D(bench)

    return bench


if __name__ == "__main__":
    run_levels().report.show()
