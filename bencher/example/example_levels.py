import bencher as bch
from bencher.utils import int_to_col

import math
import holoviews as hv
from typing import Any
import panel as pn


class LevelsExample(bch.ParametrizedSweep):
    xval = bch.FloatSweep(bounds=[0, 3.14])
    yval = bch.FloatSweep(bounds=[0, 3.14])
    level = bch.IntSweep(default=1, bounds=[1, 6])

    output = bch.ResultVar(units="v")

    def __call__(self, **kwargs: Any) -> Any:
        self.update_params_from_kwargs(**kwargs)
        self.output = math.sin(self.xval) + math.cos(self.yval)
        pt = hv.Points((self.xval, self.yval)).opts(
            marker="o", size=110 - self.level * 20, color=int_to_col(self.level - 1)
        )
        # .opts(show_legend=False,label=self.level)

        return self.get_results_values_as_dict(pt)


class RunWithLevel(bch.ParametrizedSweep):
    level = bch.IntSweep(default=1, bounds=[1, 3])
    dimensions = bch.IntSweep(default=1, bounds=[1, 2])

    level_samples = bch.ResultVar()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        # print(self.level)
        run_cfg = bch.BenchRunner.setup_run_cfg(level=self.level)
        run_cfg.auto_plot = False
        # bench = bch.Bench("Bencher_Example_Levels", PlotFunctions(), run_cfg=run_cfg)
        # res = bench.plot_sweep(
        #     title=f"Running with level: {run_cfg.level}",
        #     input_vars=[PlotFunctions.param.level_in.with_level(run_cfg.level)],
        # )

        bench_level = bch.Bench("lvl", LevelsExample(), run_cfg=run_cfg)

        res = bench_level.plot_sweep(
            f"lvl:{self.level}",
            input_vars=[
                LevelsExample.param.xval.with_level(self.level),
                LevelsExample.param.yval.with_level(self.level),
            ],
            const_vars=LevelsExample.get_input_defaults(
                [LevelsExample.param.level.with_const(self.level)]
            ),
        )

        # bench_level.append_tab(res.to_holomap().overlay())

        # bench_level.show()

        # bench = example_levels(bch.BenchRunner.setup_run_cfg(bch.BenchRunCfg(auto_plot=False), level=self.level))

        self.level_samples = int(
            pow(
                len(bch.FloatSweep(bounds=[0, 1]).with_level(self.level).values(False)),
                self.dimensions,
            )
        )

        return self.get_results_values_as_dict(res.to_holomap().overlay())
        # return self.get_results_values_as_dict(res.to(hv.Bars, bch.ReduceType.SQUEEZE))


def to_bench(class_instance):
    bench = bch.Bench(f"bench_{class_instance.name}", class_instance)
    bench.plot_sweep(f"bench_{class_instance.name}")
    bench.show()
    return bench


if __name__ == "__main__":
    bench = bch.Bench("Levels", LevelsExample())

    from holoviews import opts

    hv.extension("bokeh")
    opts.defaults(
        # opts.Curve(width=600, height=600, show_legend=False),
        opts.Curve(show_legend=False),
        # opts.Points(width=400, height=200, show_legend=False),
        opts.Points(show_legend=False),
    )

    def run_with_dim(dims):
        results = []
        for level in range(1, 6):
            print(level)
            res = bench.plot_sweep(
                f"Level:{level}",
                input_vars=dims,
                const_vars=LevelsExample.get_input_defaults(
                    [LevelsExample.param.level.with_const(level)]
                ),
                result_vars=[LevelsExample.param.output],
                run_cfg=bch.BenchRunCfg(level=level, auto_plot=False),
            )

            results.append(res)
        return results

    results = run_with_dim([LevelsExample.param.xval])
    bench.append_markdown("# Using Levels to define sample density", "Levels")
    # col = pn.Column()

    combined_pts = hv.Overlay()
    combined_curve = hv.Overlay()
    for lvl, r in enumerate(results):
        # row.append
        row = pn.Row()

        pts = r.to_holomap().overlay().opts(height=300)
        crv = r.to_curve().opts(shared_axes=False, height=300) * r.to_hv_dataset().to(
            hv.Scatter
        ).opts(size=5, height=300, shared_axes=False)

        combined_pts *= pts
        combined_curve *= crv
        row.append(pts)
        row.append(crv)
        bench.append_markdown(f"## {r.title}")
        bench.append(row)

    bench.append_markdown(
        "This plot overlays the previous plots into a single image. It shows how each level overlaps the previous level"
    )

    bench.append(pn.Row(combined_pts, combined_curve))
    # bench.show()

    results = run_with_dim([LevelsExample.param.xval, LevelsExample.param.yval])
    bench.append_markdown("# Using Levels to define 2D sample density", "Levels 2D")
    for lvl, r in enumerate(results):
        row = pn.Row()
        row.append(r.to_holomap().overlay())
        row.append(r.to_heatmap())
        bench.append(row)

    bench.append_markdown(
        "This plot overlays the previous plots into a single image. It shows how each level overlaps the previous level"
    )
    overlay = hv.Overlay()
    for lvl, r in enumerate(results):
        overlay *= r.to_holomap().overlay().opts(width=1000, height=1000, show_legend=False)

    bench.append(overlay)
    bench.show()

    # bench1 = bch.Bench("lol", PlotFunctions())

    # res = bench1.plot_sweep("lol",input_vars=[PlotFunctions.param.x_val])

    # # bench1.append(res.to(hv.Bars))
    # # bench1.append(res.to(hv.Scatter))
    # # bench1.append(res.to_scatter())
    # bench1.append(res.to_holomap().overlay())

    # bench1.show()

    # runner.run(0)
    # runner.show()

    # example_levels()

    # explorer = RunWithLevel()

    # explorer.__call__()

    # bench = to_bench(RunWithLevel())

    bench = bch.Bench("lol", RunWithLevel())

    res = bench.plot_sweep("Levels", input_vars=[RunWithLevel.param.level])

    bench.append(res.to_table())
    bench.append(res.to_curve())
    bench.append(res.to_holomap().overlay())

    bench.show()

    # bench = bch.Bench("run_with_level", RunWithLevel())

    # bench.plot_sweep("Level Vs Samples", input_vars=[RunWithLevel.param.level])

    # bench.show()

    # RunWithLevel.bench()
    # bench = None
    # for lvl in range(0, 7):
    #     bench = example_levels(bch.BenchRunner.setup_run_cfg(level=lvl), bench)

    # bench.show()
    # example_levels(ex_run_cfg).show()
