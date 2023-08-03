# pylint: disable=duplicate-code
import bencher as bch
from bencher import Bench, BenchRunCfg

# All the examples will be using the data structures and benchmark function defined in this file
from bencher.example.benchmark_data import (
    ExampleBenchCfgIn,
    ExampleBenchCfgOut,
    NoiseDistribution,
    bench_function,
)


def example_floats2D(run_cfg: BenchRunCfg) -> Bench:
    """Example of how to perform a 2D floating point parameter sweep

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """
    bench = Bench(
        "Bencher_Example_Floats",
        bench_function,
        ExampleBenchCfgIn,
        plot_lib=bch.PlotLibrary.default(),
    )

    cfg = ExampleBenchCfgIn()
    cfg.param.theta.samples = 3
    cfg.param.offset.samples = 2
    # TODO Create a test to confirm behavior

    run_cfg.use_optuna = True

    bench.plot_sweep(
        input_vars=[cfg.param.theta, cfg.param.offset],
        result_vars=[ExampleBenchCfgOut.param.out_sin, ExampleBenchCfgOut.param.out_cos],
        const_vars=[
            (cfg.param.sigma, 0.1),
            (cfg.param.noise_distribution, NoiseDistribution.gaussian),
            (cfg.param.noisy, True),
        ],
        title="Float 2D Example",
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
        input_vars=[cfg.param.theta, cfg.param.offset, cfg.param.postprocess_fn],
        result_vars=[ExampleBenchCfgOut.param.out_sin, ExampleBenchCfgOut.param.out_cos],
        const_vars=[
            (cfg.param.sigma, 0.1),
            (cfg.param.noise_distribution, NoiseDistribution.gaussian),
            (cfg.param.noisy, True),
        ],
        title="Float 2D with categorical Example",
        description="""Here we add plot a 2d surface and facet over a categorical variable
        """,
        run_cfg=run_cfg,
    )

    bench.plot_sweep(
        input_vars=[
            cfg.param.theta,
            cfg.param.offset,
            cfg.param.postprocess_fn,
            cfg.param.noise_distribution,
        ],
        result_vars=[ExampleBenchCfgOut.param.out_sin, ExampleBenchCfgOut.param.out_cos],
        const_vars=[
            (cfg.param.sigma, 0.1),
            (cfg.param.noise_distribution, NoiseDistribution.gaussian),
            (cfg.param.noisy, True),
        ],
        title="Float 2D with categorical x2 Example",
        description="""Here we add plot a 2d surface and facet over two categorical variable
        """,
        run_cfg=run_cfg,
    )

    return bench


if __name__ == "__main__":
    ex_run_cfg = BenchRunCfg()
    ex_run_cfg.repeats = 1
    example_floats2D(ex_run_cfg).plot()
