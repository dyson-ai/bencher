"""This file has some examples for how to perform basic benchmarking parameter sweeps"""

import math
import bencher as bch
import random
import panel as pn


class SimpleFloat0D(bch.ParametrizedSweep):
    """This class has 0 input dimensions and 1 output dimensions.  It samples from a gaussian distribution"""

    output = bch.ResultVar(units="ul", doc="a sample from a gaussian distribution")

    def __call__(self, **kwargs) -> dict:
        """Generate a sample from a uniform distribution

        Returns:
            dict: a dictionary with all the result variables in the ParametrisedSweep class as named key value pairs.
        """

        self.output = random.gauss()
        return super().__call__(**kwargs)


def example_0D(run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None) -> bch.Bench:
    """This example shows how to sample a 1 dimensional float variable and plot the result of passing that parameter sweep to the benchmarking function"""

    bench = SimpleFloat0D().to_bench(run_cfg, report)

    # bench.plot_sweep(plot_callbacks=False)
    bench.plot_sweep()

    res = bench.get_result()
    ds = bench.get_ds()

    bench.report.append(
        ds.hvplot(
            kind="hist",
            y=["output"],
            legend="bottom_right",
            widget_location="bottom",
        )
    )
    # bench.report.append(res.to_explorer())

    return bench


if __name__ == "__main__":
    run_config = bch.BenchRunCfg(repeats=100)
    example_0D(run_config).report.show()
