# pylint: disable=duplicate-code

from bencher.bencher import Bench, BenchRunCfg

# All the examples will be using the data structures and benchmark function defined in this file
from bencher.example.benchmark_data import ExampleBenchCfgIn, ExampleBenchCfgOut, bench_function


def example_pareto(run_cfg: BenchRunCfg) -> Bench:
    """Example of how to calculate the pareto front of a parameter sweep

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """
    bench = Bench("Multi-objective optimisation", bench_function, ExampleBenchCfgIn)

    run_cfg.use_optuna = True

    bench = bench.plot_sweep(
        title="Pareto Optimisation with Optuna",
        description="This example shows how to plot the pareto front of the tradeoff between multiple criteria.  When multiple result variable are defined, and use_optuna=True a pareto plot and the relative importance of each input variable on the output criteria is plotted. A summary of the points on the pareto front is printed as well.  You can use the pareto plot to decide the how to trade off one objective for another.  Pareto plots are suppored for 2D and 3D.  If you have more than 3 result variables the first 3 are selected for the pareto plot.  Plotting 4D surfaces is left as an exercise to the reader",
        input_vars=[
            ExampleBenchCfgIn.param.theta,
            ExampleBenchCfgIn.param.offset,
        ],
        result_vars=[ExampleBenchCfgOut.param.out_sin, ExampleBenchCfgOut.param.out_cos],
        post_description="""# Post Description 
This is a slightly unusual way of doing pareto optimisation as we are not using a typical multi-objective optimisation algorithm [TODO, add example].  Instead we are performing a grid search and looking at the resulting pareto plot.  The reason for doing a grid search instead of standard pareto optimisation is that we can produce more isolated plots of how an input affects an output which can help understanding of the parameter space.  Future examples will show how to use grid search to bootstrap further optimisation with a multi objective optimiser""",
        run_cfg=run_cfg,
    )
    return bench


if __name__ == "__main__":
    ex_run_cfg = BenchRunCfg()
    ex_run_cfg.repeats = 1
    ex_run_cfg.print_pandas = True
    ex_run_cfg.over_time = True
    example_pareto(ex_run_cfg).plot()
