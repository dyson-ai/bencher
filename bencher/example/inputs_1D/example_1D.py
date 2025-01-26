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

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        self.output = DataSource().call(self.index, kwargs["repeat"])
        return super().__call__(**kwargs)


def example_1D_float_repeats(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:
    """This example shows how to sample a 1 dimensional float variable and plot the result of passing that parameter sweep to the benchmarking function"""

    bench = Example1D().to_bench(run_cfg, report)
    bench.run_cfg = bch.BenchRunCfg(repeats=4)
    bench.plot_sweep(pass_repeat=True)

    return bench


if __name__ == "__main__":
    example_1D_float_repeats().report.show()
