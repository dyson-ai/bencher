import bencher as bch
from bencher.utils import int_to_col

import math
import holoviews as hv
from typing import Any
import panel as pn


class PlotFunctions(bch.ParametrizedSweep):
    # phase = bch.FloatSweep(
    #     default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=5
    # )

    # freq = bch.FloatSweep(default=1, bounds=[0, math.pi], doc="Input angle", units="rad", samples=5)

    # theta = bch.FloatSweep(
    #     default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=10
    # )
    # level_in = bch.IntSweep(default=0, bounds=[0, 5])

    # x_val = bch.FloatSweep(bounds=[0, 1])
    # level_in = bch.IntSweep(default=0, bounds=[0, 5])
    level_in = bch.FloatSweep(default=0, bounds=[0, 5])

    level_out = bch.ResultVar(units="v", doc="sin of theta with some noise")

    def __call__(self, plot=True, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)
        # self.level_out = self.level_in

        self.level_out = math.sin(self.level_in)

        return self.get_results_values_as_dict()

        return self.get_results_values_as_dict(hv.Scatter([self.x_val, self.level_in]))


class Level2D(bch.ParametrizedSweep):
    xval = bch.FloatSweep(bounds=[0, 1])
    yval = bch.FloatSweep(bounds=[0, 1])
    level = bch.IntSweep(bounds=[0, 6])

    level_out = bch.ResultVar(units="lvl")

    def __call__(self, **kwargs: Any) -> Any:
        self.update_params_from_kwargs(**kwargs)

        self.level_out = self.level
        size = 100 - self.level * 20
        pt = (
            hv.Points((self.xval, self.yval)).opts(
                marker="o", size=size, color=int_to_col(self.level), clabel="1"
            )
            # .opts(show_legend=False,label=self.level)
        )
        return self.get_results_values_as_dict(pt)
        # return super().__call__(*args, **kwds)


class RunWithLevel(bch.ParametrizedSweep):
    level = bch.IntSweep(default=0, bounds=[0, 2])
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

        bench_level = bch.Bench("lvl", Level2D(), run_cfg=run_cfg)

        res = bench_level.plot_sweep(
            f"lvl:{self.level}",
            input_vars=[
                Level2D.param.xval.with_level(self.level),
                Level2D.param.yval.with_level(self.level),
            ],
            const_vars=Level2D.get_input_defaults([Level2D.param.level.with_const(self.level)]),
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
    bench = bch.Bench("lvl", Level2D(), run_cfg=bch.BenchRunCfg(auto_plot=False))

    results = []
    for level in range(4):
        res = bench.plot_sweep(
            f"lvl:{level}",
            input_vars=[
                Level2D.param.xval.with_level(level),
                Level2D.param.yval.with_level(level),
                # Level2D.param.level,
            ],
            const_vars=Level2D.get_input_defaults([Level2D.param.level.with_const(level)]),
        )

        results.append(res)

        # bench_level.append_tab(res.to_holomap().overlay().opts(show_legend=False))

    bench.append_markdown("# Using Levels to define sample density", "Levels")
    row = pn.Row()
    for lvl, r in enumerate(results):
        row.append(r.to_holomap().overlay().opts(width=400, height=400, show_legend=False))
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
