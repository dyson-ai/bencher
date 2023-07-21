"""This file has some examples for how to perform basic benchmarking parameter sweeps"""

import bencher as bch
import holoviews as hv

# All the examples will be using the data structures and benchmark function defined in this file
from bencher.example.benchmark_data import ExampleBenchCfgIn, ExampleBenchCfgOut, bench_function


def example_1D_bool(run_cfg: bch.BenchRunCfg) -> bch.Bench:
    """This example shows how to sample a 1 dimensional categorical variable and plot the result of passing that parameter sweep to the benchmarking function

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """

    bencher = bch.Bench(
        "benchmarking_example_categorical1D",
        bench_function,
        ExampleBenchCfgIn,
        plot_lib=bch.PlotLibrary.default()
        # .remove(bch.PlotTypes.bar_hv)
        .remove(bch.PlotTypes.scatter_hv),
    )

    # here we sample the input variable theta and plot the value of output1. The (noisy) function is sampled 20 times so you can see the distribution
    res = bencher.plot_sweep(
        title="Example 1D Categorical",
        input_vars=[ExampleBenchCfgIn.param.noisy],
        # result_vars=[ExampleBenchCfgOut.param.out_sin, ExampleBenchCfgOut.param.out_bool],
        result_vars=[ExampleBenchCfgOut.param.out_sin],
        description=example_1D_bool.__doc__,
        run_cfg=run_cfg,
    )

    bencher.append(res.ds)
    bencher.append(res.get_dataframe())
    bencher.append(res.get_dataframe(False))

    ds = res.ds
    # print("alskdjfaslkjfslakdjflskjdf")
    # print(ds.coords.dtypes)
    # ds.coords["noisy"].dtype = int

    # print(ds.coords.dtypes)

    hvhs = hv.Dataset(ds)
    hvhs2 = hv.Dataset(res.get_dataframe(False))

    bencher.append(hvhs.to(hv.Table))

    bencher.append(hvhs2.to(hv.Table))


    # bencher.append(hv.Dataset(ds).to(hv.Table))

    # bencher.append(res.get_hv_dataset().to(hv.Table))
    # bencher.append(res.get_hv_dataset(True).to(hv.Table))
    # bencher.append(res.get_hv_dataset(False).to(hv.Table))
    # bencher.append(res.get_hv_dataset(False).to(hv.Bars))
    return bencher


if __name__ == "__main__":
    ex_run_cfg = bch.BenchRunCfg()
    ex_run_cfg.repeats = 3
    ex_run_cfg.print_pandas = True
    ex_run_cfg.over_time = False

    example_1D_bool(ex_run_cfg).plot()
