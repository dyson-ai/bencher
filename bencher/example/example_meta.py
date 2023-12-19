from typing import Any
import bencher as bch
import numpy as np
import panel as pn

from enum import auto
from strenum import StrEnum
import random
from functools import partial


class NoiseDistribution(StrEnum):
    """A categorical variable describing the types of random noise"""

    uniform = auto()  # uniform random noiase
    gaussian = auto()  # gaussian noise

    @staticmethod
    def calculate_noise(noisy, noise_distribution, sigma) -> float:
        if noisy:
            match noise_distribution:
                case NoiseDistribution.uniform:
                    return random.uniform(0, sigma)
                case NoiseDistribution.gaussian:
                    return random.gauss(0, sigma)
        return 0.0


class BenchableObject(bch.ParametrizedSweep):
    """A class to represent a 3D point in space."""

    # floating point variables
    float1 = bch.FloatSweep(default=0, bounds=[0, 1.0], doc="x coordinate of the sample volume")
    float2 = bch.FloatSweep(default=0, bounds=[0, 1.0], doc="y coordinate of the sample volume")
    float3 = bch.FloatSweep(default=0, bounds=[0, 1.0], doc="z coordinate of the sample volume")

    sigma = bch.FloatSweep(default=5, bounds=[1, 10], doc="standard deviation of the added noise")

    # categorial variables
    noisy = bch.BoolSweep(
        default=True, doc="Optionally add random noise to the output of the function"
    )
    noise_distribution = bch.EnumSweep(NoiseDistribution, doc=NoiseDistribution.__doc__)

    # var_string = StringSweep(["string1", "string2"])

    result_var = bch.ResultVar("ul", doc="The scalar value of the 3D volume field")

    # result_hmap = bch.ResultHmap()
    ##todo all var types

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)

        # distance to origin
        self.result_var = np.linalg.norm(np.array([self.float1, self.float2, self.float3]))

        # optionally add noise
        self.result_var += NoiseDistribution.calculate_noise(
            self.noisy, self.noise_distribution, self.sigma
        )

        return super().__call__()


class BenchMeta(bch.ParametrizedSweep):
    """This class uses bencher to display the multidimensional types bencher can represent"""

    float_vars = bch.IntSweep(
        default=1, bounds=(0, 4), doc="The number of floating point variables that are swept"
    )
    categorical_vars = bch.IntSweep(
        default=0, bounds=(0, 2), doc="The number of categorical variables that are swept"
    )
    sample_with_repeats = bch.IntSweep(default=1, bounds=(1, 2))

    sample_over_time = bch.BoolSweep(default=False)

    # plots = bch.ResultHmap()
    # plots = bch.ResultContainer()
    plots = bch.ResultReference(units="int")

    def __call__(self, **kwargs: Any) -> Any:
        self.update_params_from_kwargs(**kwargs)

        run_cfg = bch.BenchRunCfg()
        run_cfg.level = 2
        run_cfg.repeats = self.sample_with_repeats
        run_cfg.over_time = self.sample_over_time

        bench = bch.Bench("benchable", BenchableObject(), run_cfg=run_cfg)

        inputs_vars_float = [
            BenchableObject.param.float1,
            BenchableObject.param.float2,
            BenchableObject.param.float3,
            BenchableObject.param.sigma,
        ]

        inputs_vars_cat = [
            BenchableObject.param.noisy,
            BenchableObject.param.noise_distribution,
        ]

        input_vars = (
            inputs_vars_float[0 : self.float_vars] + inputs_vars_cat[0 : self.categorical_vars]
        )

        res = bench.plot_sweep(
            "test",
            input_vars=input_vars,
            result_vars=[BenchableObject.param.result_var],
            plot=False,
        )

        # bench.report.append(res.to_sweep_summary())
        # bench.report.app
        self.plots = bch.ResultReference()
        self.plots.obj = pn.Row(res.to_auto(width=300, height=300))
        # self.plots.obj = bench.report.pane
        return super().__call__()


def example_meta(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    print(run_cfg)
    bench = bch.Bench("bench_meta", BenchMeta(), report=report)

    res = bench.plot_sweep(
        title="Meta Bench",
        description="""## All Combinations of Variable Sweeps and Resulting Plots
        This uses bencher to display all the combinatios of plots bencher is able to produce""",
        input_vars=[
            BenchMeta.param.float_vars,
            BenchMeta.param.categorical_vars,
            BenchMeta.param.sample_with_repeats,
            # BenchMeta.param.sample_over_time,
        ],
        plot=False,
    )

    bench.report.append(res.to_sweep_summary())
    bench.report.append(res.to_references(container=partial(pn.Card, width=1500, height=350)))
    return bench


if __name__ == "__main__":
    example_meta().report.show()
