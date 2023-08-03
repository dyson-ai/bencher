"""This file has some examples for how to modify what plots are shown with PlotLibrary"""

import bencher as bch

# All the examples will be using the data structures and benchmark function defined in this file
from bencher.example.benchmark_data import ExampleBenchCfgIn, ExampleBenchCfgOut, bench_function


def example_plot_library(run_cfg: bch.BenchRunCfg) -> bch.Bench:
    """This example shows how use PlotLibrary.all() to display all possible plot types for a given benchmark

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """

    bencher = bch.Bench("benchmarking_example_categorical1D", bench_function, ExampleBenchCfgIn)

    plot_lib = bch.PlotLibrary.all()

    bencher.plot_sweep(
        title="Example 1D Categorical",
        input_vars=[ExampleBenchCfgIn.param.postprocess_fn],
        const_vars=[(ExampleBenchCfgIn.param.noisy, True)],
        result_vars=[ExampleBenchCfgOut.param.out_cos, ExampleBenchCfgOut.param.out_sin],
        description=example_plot_library.__doc__,
        run_cfg=run_cfg,
        plot_lib=plot_lib,
    )

    bencher.plot_sweep(
        title="Example 1D Float",
        input_vars=[ExampleBenchCfgIn.param.theta],
        const_vars=[(ExampleBenchCfgIn.param.noisy, True)],
        result_vars=[ExampleBenchCfgOut.param.out_cos, ExampleBenchCfgOut.param.out_sin],
        description=example_plot_library.__doc__,
        run_cfg=run_cfg,
        plot_lib=plot_lib,
    )

    bencher.plot_sweep(
        title="Example Float Cat Single",
        input_vars=[ExampleBenchCfgIn.param.theta, ExampleBenchCfgIn.param.postprocess_fn],
        const_vars=[(ExampleBenchCfgIn.param.noisy, True)],
        result_vars=[ExampleBenchCfgOut.param.out_cos, ExampleBenchCfgOut.param.out_sin],
        description=example_plot_library.__doc__,
        run_cfg=bch.BenchRunCfg(repeats=1),
        plot_lib=plot_lib,
    )

    bencher.plot_sweep(
        title="Example Float Cat Repeats",
        input_vars=[ExampleBenchCfgIn.param.theta, ExampleBenchCfgIn.param.postprocess_fn],
        const_vars=[(ExampleBenchCfgIn.param.noisy, True)],
        result_vars=[ExampleBenchCfgOut.param.out_cos, ExampleBenchCfgOut.param.out_sin],
        description=example_plot_library.__doc__,
        run_cfg=run_cfg,
        plot_lib=plot_lib,
    )

    return bencher


if __name__ == "__main__":
    ex_run_cfg = bch.BenchRunCfg()
    ex_run_cfg.repeats = 5
    example_plot_library(ex_run_cfg).plot()
