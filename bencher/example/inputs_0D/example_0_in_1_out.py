"""This file has some examples for how to perform basic benchmarking parameter sweeps"""

import bencher as bch
import random


class SimpleFloat0D(bch.ParametrizedSweep):
    """This class has 0 input dimensions and 1 output dimensions.  It samples from a gaussian distribution"""

    # This defines a variable that we want to plot
    output = bch.ResultVar(units="ul", doc="a sample from a gaussian distribution")

    def __call__(self, **kwargs) -> dict:
        """Generate a sample from a uniform distribution

        Returns:
            dict: a dictionary with all the result variables in the ParametrisedSweep class as named key value pairs.
        """

        self.output = random.gauss(mu=0.0, sigma=1.0)
        return super().__call__(**kwargs)


def example_0_in_1_out(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:
    """This example shows how to sample a 1 dimensional float variable and plot the result of passing that parameter sweep to the benchmarking function"""

    bench = SimpleFloat0D().to_bench(run_cfg, report)
    bench.plot_sweep()

    bench.report.append(bench.get_result().to_table())
    return bench


if __name__ == "__main__":
    run_config = bch.BenchRunCfg(repeats=100)
    reprt = bch.BenchReport()
    # example_0_in_1_out(run_cfg, report).report.show()

    # run_cfg.over_time = True
    # run_cfg.cache_samples = True
    # for i in range(4):
    #     example_0_in_1_out(run_cfg, report)

    run_config.over_time = True
    run_config.auto_plot = False
    for _ in range(4):
        example_0_in_1_out(run_config, reprt)

    run_config.auto_plot = True
    example_0_in_1_out(run_config, reprt)

    reprt.show()
