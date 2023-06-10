"""This file has some examples for how to perform basic benchmarking parameter sweeps"""

from bencher.bencher import Bench, BenchRunCfg

# All the examples will be using the data structures and benchmark function defined in this file
from bencher.example.benchmark_data import ExampleBenchCfgIn, ExampleBenchCfgOut, bench_function


def example_1D_cat(run_cfg: BenchRunCfg) -> Bench:
    """This example shows how to sample a 1 dimensional categorical variable and plot the result of passing that parameter sweep to the benchmarking function

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """

    bencher = Bench("benchmarking_example_categorical1D", bench_function, ExampleBenchCfgIn)

    # here we sample the input variable theta and plot the value of output1. The (noisy) function is sampled 20 times so you can see the distribution
    bencher.plot_sweep(
        title="Example 1D Categorical",
        input_vars=[ExampleBenchCfgIn.param.postprocess_fn],
        result_vars=[ExampleBenchCfgOut.param.out_cos, ExampleBenchCfgOut.param.out_sin],
        description=example_1D_cat.__doc__,
        run_cfg=run_cfg,
    )
    return bencher


if __name__ == "__main__":
    ex_run_cfg = BenchRunCfg()
    ex_run_cfg.repeats = 10
    ex_run_cfg.print_pandas = True
    ex_run_cfg.over_time = True

    example_1D_cat(ex_run_cfg).plot()
