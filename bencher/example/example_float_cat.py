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

    ExampleBenchCfgIn.param.theta.samples = 3

    bench.plot_sweep(
        input_vars=[
            ExampleBenchCfgIn.param.theta,
            ExampleBenchCfgIn.param.offset,
            ExampleBenchCfgIn.param.postprocess_fn,
        ],
        result_vars=[ExampleBenchCfgOut.param.out_sin],
        const_vars=[(ExampleBenchCfgIn.param.noisy, True)],
        title="Float 2D Cat 1D Example",
        description="""Following from the previous example lets add another input parameter to see how that affects the output.  We pass the boolean  'noisy' and keep the other parameters the same""",
        post_description="Now the plot has two lines, one for each of the boolean values where noisy=true and noisy=false.",
        run_cfg=run_cfg,
    )

    bench.plot_sweep(
        input_vars=[ExampleBenchCfgIn.param.theta],
        result_vars=[ExampleBenchCfgOut.param.out_sin],
        const_vars=[(ExampleBenchCfgIn.param.noisy, True)],
        title="Float 1D Cat 1D  Example",
        description="""Following from the previous example lets add another input parameter to see how that affects the output.  We pass the boolean  'noisy' and keep the other parameters the same""",
        post_description="Now the plot has two lines, one for each of the boolean values where noisy=true and noisy=false.",
        run_cfg=run_cfg,
    )

    # this does not work yet because it tries to find min and max of categorical values
    # bench.plot_sweep(
    #     input_vars=[ExampleBenchCfgIn.param.theta, ExampleBenchCfgIn.param.postprocess_fn],
    #     result_vars=[ExampleBenchCfgOut.param.out_sin],
    #     const_vars=[(ExampleBenchCfgIn.param.noisy, True)],
    #     title="Float 1D Cat 1D  Example",
    #     description="""Following from the previous example lets add another input parameter to see how that affects the output.  We pass the boolean  'noisy' and keep the other parameters the same""",
    #     post_description="Now the plot has two lines, one for each of the boolean values where noisy=true and noisy=false.",
    #     run_cfg=run_cfg,
    # )

    return bench


if __name__ == "__main__":
    import time

    ex_run_cfg = BenchRunCfg()
    ex_run_cfg.repeats = 2
    ex_run_cfg.over_time = True
    # ex_run_cfg.debug = True
    # ex_run_cfg.print_pandas = True
    ex_run_cfg.clear_cache = True
    ex_run_cfg.clear_history = True
    ex_run_cfg.time_event = "run 1"
    ex_run_cfg.use_optuna = True
    # ex_run_cfg.time_src = str(datetime.now())

    example_cat_float(ex_run_cfg)

    time.sleep(1)

    ex_run_cfg.clear_cache = False
    ex_run_cfg.clear_history = False
    ex_run_cfg.time_event = "run 2"
    # ex_run_cfg.time_src = str(datetime.now())

    example_cat_float(ex_run_cfg)
    time.sleep(1)

    ex_run_cfg.time_event = "run 3"
    # ex_run_cfg.time_src = str(datetime.now())
    example_cat_float(ex_run_cfg).plot()
