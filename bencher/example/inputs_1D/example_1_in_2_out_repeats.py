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
        return self.data[index][repeat - 1]


class Example1D(bch.ParametrizedSweep):
    index = bch.IntSweep(default=0, bounds=[0, 5], doc="Input angle", units="rad", samples=30)
    output = bch.ResultVar(units="v", doc="sin of theta")
    output2 = bch.ResultVar(units="v", doc="-sin of theta")

    def __init__(self, **params):
        super().__init__(**params)
        self.data1 = DataSource()
        self.data2 = DataSource()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        self.output = self.data1.call(self.index)
        self.output2 = -self.data2.call(self.index)
        return super().__call__(**kwargs)


def example_1_in_2_out_repeats(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:
    """This example shows how to sample a 1 dimensional float variable and plot the result of passing that parameter sweep to the benchmarking function"""

    from importlib.metadata import version

    print(version("holobench"))
    if run_cfg is None:
        run_cfg = bch.BenchRunCfg()
    run_cfg.repeats = 4
    bench = Example1D().to_bench(run_cfg, report)
    bench.plot_sweep()
    return bench


if __name__ == "__main__":
    run_config = bch.BenchRunCfg()
    reprt = bch.BenchReport()
    example_1_in_2_out_repeats(run_config, reprt)
    reprt.show()
