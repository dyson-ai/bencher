import bencher as bch
from bencher.example.inputs_1D.example1d_common import Example1D


def example_1_in_2_out_repeats(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:
    """This example shows how to sample a 1 dimensional float variable and plot the result of passing that parameter sweep to the benchmarking function"""
    run_cfg.repeats = 4
    bench = Example1D().to_bench(run_cfg, report)
    bench.plot_sweep()
    return bench


if __name__ == "__main__":
    run_config = bch.BenchRunCfg()
    reprt = bch.BenchReport()
    example_1_in_2_out_repeats(run_config, reprt)
    reprt.show()
