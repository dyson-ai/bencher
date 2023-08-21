import bencher as bch


import math


class PlotFunctions(bch.ParametrizedSweep):
    phase = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=5
    )

    freq = bch.FloatSweep(default=1, bounds=[0, math.pi], doc="Input angle", units="rad", samples=5)

    theta = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=10
    )

    fn_output = bch.ResultVar(units="v", doc="sin of theta with some noise")

    def __call__(self, plot=True, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)
        self.fn_output = math.sin(self.phase + self.freq * self.theta)
        return self.get_results_values_as_dict()


def example_levels(run_cfg: bch.BenchRunCfg, bench=None) -> bch.Bench:
    if bench is None:
        bench = bch.Bench("Bencher_Example_Levels", PlotFunctions, run_cfg=run_cfg)

    # run_cfg.auto_plot = False
    res = bench.plot_sweep(
        title=f"Running with level: {run_cfg.level}",
        input_vars=[PlotFunctions.param.phase.with_level(run_cfg.level)],
    )

    # bench.append(res.to_scatter())

    return bench


class RunWithLevel(bch.ParametrizedSweep):
    level = bch.IntSweep(default=0, bounds=[0, 6])

    level_samples = bch.ResultVar()

    def __call__(self, level):
        run_cfg = bch.BenchRunner.setup_run_cfg(level=level)
        run_cfg.auto_plot = False
        bench = bch.Bench("Bencher_Example_Levels", PlotFunctions, run_cfg=run_cfg)
        res = bench.plot_sweep(
            title=f"Running with level: {run_cfg.level}",
            input_vars=[PlotFunctions.param.phase.with_level(run_cfg.level)],
        )
        # bench = example_levels(bch.BenchRunner.setup_run_cfg(bch.BenchRunCfg(auto_plot=False) level=level))

        return self.get_results_values_as_dict(res.to_curve())


if __name__ == "__main__":
    # runner = bch.BenchRunner()

    # runner.add_run(example_levels)

    # runner.run(0)
    # runner.show()

    # example_levels()

    RunWithLevel.bench()
    bench = None
    for lvl in range(0, 7):
        bench = example_levels(bch.BenchRunner.setup_run_cfg(level=lvl), bench)

    bench.show()
    # example_levels(ex_run_cfg).show()
