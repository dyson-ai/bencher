import bencher as bch
import math
import random
import numpy as np
import holoviews as hv


class PlotFunctions(bch.ParametrizedSweep):

    end = bch.FloatSweep(default=0, bounds=[0, 1])

    # RESULT VARS
    ref = bch.ResultReference()

    def __call__(self, plot=True, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)

        print("I am getting called")

        plot = hv.Curve([(0, 0), (1, self.end)])

        self.ref = bch.ResultReference(plot)

        return self.get_results_values_as_dict()

    def plot_holo(self, plot=True) -> hv.core.ViewableElement:
        """Plots a generic representation of the object that is not a basic hv datatype. In this case its an image of the values of the object, but it could be any representation of the object, e.g. a screenshot of the object state"""
        if plot:
            pt = hv.Text(0, 0, f"{self.phase}\n{self.freq}\n {self.theta}")
            pt *= hv.Ellipse(0, 0, 1)
            return pt
        return None


def example_plots(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    bench = PlotFunctions().to_bench(run_cfg, report)

    bench.plot_sweep()

    return bench


if __name__ == "__main__":
    bench_run = bch.BenchRunner("bench_runner_test")
    bench_run.add_run(example_plots)

    bench_run.run(3, 3, show=True,use_cache=False)
