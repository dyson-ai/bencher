import bencher as bch


import math
import holoviews as hv
from typing import Any


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
    level = bch.IntSweep(bounds=[0, 3])

    def __call__(self, **kwargs: Any) -> Any:
        self.update_params_from_kwargs(**kwargs)

        pt = hv.Points((self.xval, self.yval)).opts(marker="o", size=self.level)
        return self.get_results_values_as_dict(pt)
        # return super().__call__(*args, **kwds)


class RunWithLevel(bch.ParametrizedSweep):
    level = bch.IntSweep(default=0, bounds=[0, 5])
    dimensions = bch.IntSweep(default=1, bounds=[1, 2])

    level_samples = bch.ResultVar()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        # print(self.level)
        run_cfg = bch.BenchRunner.setup_run_cfg(level=self.level)
        run_cfg.auto_plot = False
        bench = bch.Bench("Bencher_Example_Levels", PlotFunctions(), run_cfg=run_cfg)
        res = bench.plot_sweep(
            title=f"Running with level: {run_cfg.level}",
            input_vars=[PlotFunctions.param.level_in.with_level(run_cfg.level)],
        )
        # bench = example_levels(bch.BenchRunner.setup_run_cfg(bch.BenchRunCfg(auto_plot=False), level=self.level))

        self.level_samples = int(
            pow(
                len(bch.FloatSweep(bounds=[0, 1]).with_level(self.level).values(False)),
                self.dimensions,
            )
        )

        # return self.get_results_values_as_dict()
        return self.get_results_values_as_dict(res.to(hv.Bars, bch.ReduceType.SQUEEZE))


def to_bench(class_instance):
    bench = bch.Bench(f"bench_{class_instance.name}", class_instance)
    bench.plot_sweep(f"bench_{class_instance.name}")
    bench.show()
    return bench


if __name__ == "__main__":
    # to_bench(PlotFunctions())

    to_bench(Level2D)

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

    bench = bch.Bench("lol", RunWithLevel(), plot_lib=bch.PlotLibrary.no_plotly())

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
