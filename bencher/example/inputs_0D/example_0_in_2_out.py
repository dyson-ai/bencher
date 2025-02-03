"""This file has some examples for how to perform basic benchmarking parameter sweeps"""

import bencher as bch
import random


class SimpleFloat0D(bch.ParametrizedSweep):
    """This class has 0 input dimensions and 1 output dimensions.  It samples from a gaussian distribution"""

    # This defines a variable that we want to plot
    output1 = bch.ResultVar(units="ul", doc="a sample from a gaussian distribution")
    output2 = bch.ResultVar(units="ul", doc="a sample from a gaussian distribution")

    def __call__(self, **kwargs) -> dict:
        """Generate a sample from a uniform distribution

        Returns:
            dict: a dictionary with all the result variables in the ParametrisedSweep class as named key value pairs.
        """

        self.output1 = random.gauss(mu=0.0, sigma=1.0)
        self.output2 = random.gauss(mu=2.0, sigma=5.0)
        return super().__call__(**kwargs)


def example_0_in_2_out(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:
    """This example shows how to sample a 1 dimensional float variable and plot the result of passing that parameter sweep to the benchmarking function"""

    bench = SimpleFloat0D().to_bench(run_cfg, report)
    bench.plot_sweep()
    return bench


if __name__ == "__main__":
    run_config = bch.BenchRunCfg(repeats=500)
    example_0_in_2_out(run_config).report.show()
