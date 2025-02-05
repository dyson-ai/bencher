"""This file has some examples for how to perform basic benchmarking parameter sweeps"""

import random
import bencher as bch
import param


@param.output(bch.ResultVar(name="output", units="ul", doc="a sample from a gaussian distribution"))
def gaussian():
    """Generate a sample from a uniform distribution

    Returns:
        dict: a dictionary with all the result variables in the ParametrisedSweep class as named key value pairs.
    """
    return dict(output=random.gauss(mu=0.0, sigma=1.0))


def example_0D(run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None) -> bch.Bench:
    """This example shows how to sample a 1 dimensional float variable and plot the result of passing that parameter sweep to the benchmarking function"""

    # print(gaussian.param.method_outputs())
    # print(gaussian.param.outputs())
    bench = bch.Bench("gauss", gaussian, run_cfg=run_cfg)
    # bench.plot_sweep(result_vars=[gaussian.outputs["output"]])
    bench.plot_sweep(result_vars=[bch.ResultVar(name="output", units="ul", doc="a sample from a gaussian distribution")])
    return bench


if __name__ == "__main__":
    run_config = bch.BenchRunCfg(repeats=100)
    example_0D(run_config).report.show()
