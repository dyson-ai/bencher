"""This file has some examples for how to perform basic benchmarking parameter sweeps"""

import bencher as bch

# All the examples will be using the data structures and benchmark function defined in this file
from bencher.example.benchmark_data import ExampleBenchCfgIn, ExampleBenchCfgOut, bench_function


def example_plot_library(run_cfg: bch.BenchRunCfg) -> bch.Bench:
    """This example shows how to sample a 1 dimensional categorical variable and plot the result of passing that parameter sweep to the benchmarking function

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """

    bencher = bch.Bench("benchmarking_example_categorical1D", bench_function, ExampleBenchCfgIn)

    plot_lib = bch.PlotLibrary.default()
    plot_lib.add(bch.PlotTypes.barplot)
    plot_lib.add(bch.PlotTypes.dataframe_flat)
    plot_lib.add(bch.PlotTypes.dataframe_mean)

    plot_lib.remove(bch.PlotTypes.swarmplot)

    plot_lib = bch.PlotLibrary.all()

    # here we sample the input variable theta and plot the value of output1. The (noisy) function is sampled 20 times so you can see the distribution
    bencher.plot_sweep(
        title="Example 1D Categorical",
        input_vars=[ExampleBenchCfgIn.param.postprocess_fn],
        const_vars=[(ExampleBenchCfgIn.param.noisy, True)],
        result_vars=[ExampleBenchCfgOut.param.out_cos, ExampleBenchCfgOut.param.out_sin],
        description=example_plot_library.__doc__,
        run_cfg=run_cfg,
        plot_lib=plot_lib,
    )
    return bencher


if __name__ == "__main__":
    ex_run_cfg = bch.BenchRunCfg()
    ex_run_cfg.repeats = 10
    ex_run_cfg.print_pandas = True
    # ex_run_cfg.over_time = True

    example_plot_library(ex_run_cfg).plot()
