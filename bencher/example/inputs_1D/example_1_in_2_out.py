import bencher as bch
from bencher.example.inputs_1D.example1d_common import Example1D


def example_1_in_2_out(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:
    """This example shows how to sample a 1 dimensional float variable and plot the result of passing that parameter sweep to the benchmarking function"""
    bench = Example1D().to_bench(run_cfg, report)
    bench.plot_sweep()

    # bench.report.append(bench.get_result().to_heatmap())
    return bench


if __name__ == "__main__":
    run_config = bch.BenchRunCfg()
    reprt = bch.BenchReport()
    example_1_in_2_out(run_config, reprt)
    # run_config.over_time = True
    # run_config.auto_plot = False
    # for i in range(4):
    #     example_1_in_2_out(run_config, reprt)

    # run_config.auto_plot = True
    # example_1_in_2_out(run_config, reprt)
    reprt.show()
