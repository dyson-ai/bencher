# pylint: disable=duplicate-code

import pathlib

from bencher import Bench, BenchRunCfg

# All the examples will be using the data structures and benchmark function defined in this file
from bencher.example.benchmark_data import ExampleBenchCfgIn, ExampleBenchCfgOut, bench_function


def example_floats(run_cfg: BenchRunCfg) -> Bench:
    """Example of how to perform a parameter sweep for floating point variables

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """
    bench = Bench("Bencher_Example_Floats", bench_function, ExampleBenchCfgIn)

    rdmepath = pathlib.Path(__file__).parent.parent.parent / "README.md"
    with open(rdmepath, "r", encoding="utf-8") as file:
        readme = file.read()

    bench.plot_sweep(title="Intro", description=readme)

    bench.plot_sweep(
        input_vars=[ExampleBenchCfgIn.param.theta],
        result_vars=[ExampleBenchCfgOut.param.out_sin],
        title="Float 1D Example",
        description="""Bencher is a tool to make it easy to explore how input parameter affect a range of output metrics.  In these examples we are going to benchmark an example function which has been selected to show the features of bencher.
        The example function takes an input theta and returns the absolute value of sin(theta) and cos(theta) +- various types of noise.

        def bench_function(cfg: ExampleBenchCfgIn) -> ExampleBenchCfgOut:
            "Takes an ExampleBenchCfgIn and returns a ExampleBenchCfgOut output"
            out = ExampleBenchCfgOut()
            noise = calculate_noise(cfg)
            offset = 0.0

            postprocess_fn = abs if cfg.postprocess_fn == PostprocessFn.absolute else negate_fn

            out.out_sin = postprocess_fn(offset + math.sin(cfg.theta) + noise)
            out.out_cos = postprocess_fn(offset + math.cos(cfg.theta) + noise)
            return out

    The following examples will show how to perform parameter sweeps to characterise the behavior of the function.  The idea is that the benchmarking can be used to gain understanding of an unknown function. 
        """,
        post_description="Here you can see the output plot of sin theta between 0 and pi.  In the tabs at the top you can also view 3 tabular representations of the data",
        run_cfg=run_cfg,
    )

    bench.plot_sweep(
        input_vars=[ExampleBenchCfgIn.param.theta, ExampleBenchCfgIn.param.noisy],
        result_vars=[ExampleBenchCfgOut.param.out_sin],
        title="Float 1D and Bool Example",
        description="""Following from the previous example lets add another input parameter to see how that affects the output.  We pass the boolean  'noisy' and keep the other parameters the same""",
        post_description="Now the plot has two lines, one for each of the boolean values where noisy=true and noisy=false.",
        run_cfg=run_cfg,
    )

    bench.plot_sweep(
        input_vars=[ExampleBenchCfgIn.param.theta, ExampleBenchCfgIn.param.noisy],
        result_vars=[ExampleBenchCfgOut.param.out_sin, ExampleBenchCfgOut.param.out_cos],
        title="Float 1D and Bool Example with multiple outputs",
        description="""Following from the previous example here the second output is added to the result variables""",
        post_description="Another column is added for the result variable that shows cos(theta)",
        run_cfg=run_cfg,
    )

    bench.plot_sweep(
        input_vars=[
            ExampleBenchCfgIn.param.theta,
            ExampleBenchCfgIn.param.noisy,
            ExampleBenchCfgIn.param.postprocess_fn,
        ],
        result_vars=[
            ExampleBenchCfgOut.param.out_sin,
            ExampleBenchCfgOut.param.out_cos,
        ],
        title="Float 1D, Bool and Categorical Example",
        description="""Following from the previous example lets add another input parameter to see how that affects the output.  We add the 'postprocess_fn' categorical enum value which either takes the absolute value or negates the output of the function.""",
        post_description="This generates two rows of results, one for each of the category options.",
        run_cfg=run_cfg,
    )

    return bench


if __name__ == "__main__":
    ex_run_cfg = BenchRunCfg(repeats=10)

    example_floats(ex_run_cfg).plot()
