"""Example of how to perform a parameter sweep for categorical variables"""
from bencher import Bench, BenchRunCfg

# All the examples will be using the data structures and benchmark function defined in this file
from bencher.example.benchmark_data import ExampleBenchCfgIn, ExampleBenchCfgOut, bench_function


def example_cat_float(run_cfg: BenchRunCfg) -> Bench:
    """Example of how to perform a parameter sweep for categorical variables

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """
    bench = Bench("Bencher_Example_Float_Cat", bench_function, ExampleBenchCfgIn)


    bench.plot_sweep(
        input_vars=[
            ExampleBenchCfgIn.param.theta,
            ExampleBenchCfgIn.param.postprocess_fn,
        ],
        result_vars=[ExampleBenchCfgOut.param.out_sin],
    
        title="Float 2D Cat 1D Example",
        description="""Following from the previous example lets add another input parameter to see how that affects the output.  We pass the boolean  'noisy' and keep the other parameters the same""",
        post_description="Now the plot has two lines, one for each of the boolean values where noisy=true and noisy=false.",
        run_cfg=run_cfg,
    )



    return bench


if __name__ == "__main__":

    ex_run_cfg = BenchRunCfg()

    example_cat_float(ex_run_cfg).plot()