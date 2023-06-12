import bencher as bch

# All the examples will be using the data structures and benchmark function defined in this file
from bencher.example.benchmark_data import ExampleBenchCfgIn, ExampleBenchCfgOut, bench_function


def example_float_grouped(run_cfg: bch.BenchRunCfg) -> bch.Bench:
    """Example of how to perform a parameter sweep for floating point variables

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """
    bench = bch.Bench("Bencher_Example_Float_Cat", bench_function, ExampleBenchCfgIn)

    bench.plot_sweep(
        input_vars=[
            ExampleBenchCfgIn.param.theta,
        ],
        result_vars=[ExampleBenchCfgOut.param.out_sin, ExampleBenchCfgOut.param.out_cos],
        result_groups=[[0, 1]],
        const_vars=[(ExampleBenchCfgIn.param.noisy, True)],
        title="Float 2D Cat 1D Example",
        description="""Following from the previous example lets add another input parameter to see how that affects the output.  We pass the boolean  'noisy' and keep the other parameters the same""",
        post_description="Now the plot has two lines, one for each of the boolean values where noisy=true and noisy=false.",
        run_cfg=run_cfg,
    )

    return bench


if __name__ == "__main__":
    ex_run_cfg = bch.BenchRunCfg(repeats=10)

    example_float_grouped(ex_run_cfg).plot()
