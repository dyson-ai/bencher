"""This file has some examples for how to perform basic benchmarking parameter sweeps"""

import random
import bencher as bch


def gaussian():
    """Generate a sample from a uniform distribution

    Returns:
        dict: A sample from a gaussian distribution
    """
    return dict(output=random.gauss(mu=0.0, sigma=1.0))


def example_0D(run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None) -> bch.Bench:
    """This example shows how to sample a 1 dimensional float variable from a free function.  Most of the other examples will use parametrized class to represent the worker function as it is more flexible longterm when investigating systems with more inputs and outputs"""

    bench = bch.Bench("", gaussian, run_cfg=run_cfg)

    output = bch.ResultVar(name="output", units="v", doc="a sample from a gaussian distribution")

    bench.plot_sweep(result_vars=[output])
    return bench


if __name__ == "__main__":
    run_config = bch.BenchRunCfg(repeats=100)
    example_0D(run_config).report.show()
