"""This file has some examples for how to perform basic benchmarking parameter sweeps"""

import bencher as bch


class DataSource:
    def __init__(self):
        self.data = [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [2, 1, 1, 0],
            [2, 2, 0, 0],
            [2, 2, 1, 1],
        ]

    def call(self, index, repeat):
        return self.data[index][repeat - 1]


class Example1D(bch.ParametrizedSweep):
    index = bch.IntSweep(default=0, bounds=[0, 5], doc="Input angle", units="rad", samples=30)
    output = bch.ResultVar(units="v", doc="sin of theta")
    output2 = bch.ResultVar(units="v", doc="-sin of theta")

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        self.output = DataSource().call(self.index, kwargs["repeat"])
        self.output2 = -DataSource().call(self.index, kwargs["repeat"])
        return super().__call__(**kwargs)


def example_1D_float_repeats(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:
    """This example shows how to sample a 1 dimensional float variable and plot the result of passing that parameter sweep to the benchmarking function"""

    bench = Example1D().to_bench(run_cfg, report)
    # bench.plot_sweep(pass_repeat=True,plot_callbacks=False)

    # res = bench.get_result()
    bench.run_cfg = bch.BenchRunCfg(repeats=4)
    # bench.plot_sweep(pass_repeat=True, plot_callbacks=False)
    bench.plot_sweep(pass_repeat=True)

    res = bench.get_result()
    bench.report.append(res.to_curve(Example1D.param.output))
    # bench.report.append(res.to_curve("output"))
    # bench.report.append(hv.Table(res.to_hv_dataset(bch.ReduceType.MINMAX)))
    # bench.report.append(res.to_curve() + res.to_scatter_jitter(override=True))
    # bench.report.append(res.to_line())
    bench.report.append(res.to_scatter_jitter(override=True))
    # bench.report.append(res.to_error_bar())
    # bench.report.append(res.to_explorer())
    # bench.report.append(res.to_error_bar()

    # bench.report.append(res.to_dataset())
    # bench.report.append(res.to_xarray().hvplot.plot(kind="andrews_curves"))
    # print(res.to_xarray())
    # bench.report.append()
    return bench


if __name__ == "__main__":
    example_1D_float_repeats().report.show()
