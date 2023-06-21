import bencher as bch


class InputCfg(bch.ParametrizedSweep):
    """An example of a datatype with an integer and float parameter"""

    x = bch.FloatSweep(
        sample_values=[2, 3, 4, 7, 8, 9],
        doc="An example of a user defines set of sweep values",
    )
    y = bch.IntSweep(
        sample_values=[1, 2, 6], doc="An example of a user defines set of sweep values"
    )


class Result(bch.ParametrizedSweep):
    result = bch.ResultVar("ul", doc="Square of x")


def benchmark_fn(cfg: InputCfg) -> Result:
    output = Result()
    output.result = cfg.x * cfg.x - cfg.y * 3
    return output


def example_custom_sweep(run_cfg: bch.BenchRunCfg) -> bch.Bench:
    """This example shows how to define a custom set of value to sample from intead of a uniform sweep

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """

    bencher = bch.Bench("benchmarking_example_custom_sweep", benchmark_fn, InputCfg)

    # here we sample the input variable theta and plot the value of output1. The (noisy) function is sampled 20 times so you can see the distribution

    bencher.plot_sweep(
        title="Example User Defined Sweep 1D",
        # input_vars=[InputCfg.param.x],
        input_vars=[InputCfg.param.x],
        result_vars=[Result.param.result],
        description=example_custom_sweep.__doc__,
        run_cfg=run_cfg,
    )

    bencher.plot_sweep(
        title="Example User Defined Sweep 2D",
        # input_vars=[InputCfg.param.x],
        input_vars=[InputCfg.param.x, InputCfg.param.y],
        result_vars=[Result.param.result],
        description=example_custom_sweep.__doc__,
        run_cfg=run_cfg,
    )
    return bencher


if __name__ == "__main__":
    ex_run_cfg = bch.BenchRunCfg()
    # ex_run_cfg.debug = True
    example_custom_sweep(ex_run_cfg).plot()
