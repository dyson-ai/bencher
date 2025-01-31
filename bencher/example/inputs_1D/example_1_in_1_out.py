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

        self.call_count = [0] * len(self.data)

    def call(self, index, repeat=None):
        if repeat is None:
            self.call_count[index] += 1
            repeat = self.call_count[index]
        print(index, repeat)
        return self.data[index][repeat - 1]


class Example1D(bch.ParametrizedSweep):
    index = bch.IntSweep(default=0, bounds=[0, 5], doc="Input angle", units="rad", samples=30)
    output = bch.ResultVar(units="v", doc="sin of theta")

    def __init__(self, **params):
        super().__init__(**params)
        self.data1 = DataSource()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        self.output = self.data1.call(self.index)
        return super().__call__(**kwargs)


def example_1_in_1_out(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:
    """This example shows how to sample a 1 dimensional float variable and plot the result of passing that parameter sweep to the benchmarking function"""
    bench = Example1D().to_bench(run_cfg, report)
    bench.plot_sweep()
    return bench


if __name__ == "__main__":
    run_config = bch.BenchRunCfg()
    reprt = bch.BenchReport()
    example_1_in_1_out(run_config, reprt)

    run_config.repeats = 4
    example_1_in_1_out(run_config, reprt)

    # run_cfg.over_time = True
    # for i in range(4):
    #     example_1_in_2_out(run_cfg, report)

    reprt.show()
