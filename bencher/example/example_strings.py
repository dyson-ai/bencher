import bencher as bch


class TestPrinting(bch.ParametrizedSweep):
    # INPUTS
    a = bch.StringSweep(default=None, string_list=["a1", "a2"], allow_None=True)
    b = bch.StringSweep(default=None, string_list=["b1", "b2"], allow_None=True)
    c = bch.StringSweep(default=None, string_list=["c1", "c2"], allow_None=True)
    d = bch.StringSweep(default=None, string_list=["d1", "d2"], allow_None=True)

    # RESULTS
    result = bch.ResultString()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)

        self.result = self.a
        if self.b is not None:
            self.result += f",{self.b}"
        if self.c is not None:
            self.result += f",{self.c}"
        if self.d is not None:
            self.result += f",{self.d}"
        return super().__call__()


def example_strings(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    run_cfg.auto_plot = False

    bench = bch.Bench("strings", TestPrinting(), run_cfg=run_cfg, report=report)

    for s in [
        [TestPrinting.param.a],
        [TestPrinting.param.a, TestPrinting.param.b],
        [TestPrinting.param.a, TestPrinting.param.b, TestPrinting.param.c],
        [TestPrinting.param.a, TestPrinting.param.b, TestPrinting.param.c, TestPrinting.param.d],
    ]:
        res = bench.plot_sweep("String Panes", input_vars=s)
        bench.report.append_tab(res.to_panes())
    return bench


if __name__ == "__main__":
    example_strings().report.show()
