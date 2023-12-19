from typing import Any
import bencher as bch
import numpy as np
import panel as pn


class BenchableObject(bch.ParametrizedSweep):
    """A class to represent a 3D point in space."""

    float1 = bch.FloatSweep(
        default=0, bounds=[-1.0, 1.0], doc="x coordinate of the sample volume", samples=4
    )
    float2 = bch.FloatSweep(
        default=0, bounds=[-1.0, 1.0], doc="y coordinate of the sample volume", samples=5
    )
    float3 = bch.FloatSweep(
        default=0, bounds=[-1.0, 1.0], doc="z coordinate of the sample volume", samples=6
    )

    result_var = bch.ResultVar("ul", doc="The scalar value of the 3D volume field")
    # result_hmap = bch.ResultHmap()
    ##todo all var types

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)

        # distance to origin
        self.result_var = np.linalg.norm(np.array([self.float1, self.float2, self.float3]))

        return super().__call__()


class BenchMeta(bch.ParametrizedSweep):

    """This class uses bencher to display the multidimensional types bencher can represent"""

    categorigal_vars = bch.IntSweep(default=0, bounds=(0, 3))
    float_vars = bch.IntSweep(default=1, bounds=(1, 3))

    # input_vars_cat=[]

    # plots = bch.ResultHmap()
    # plots = bch.ResultContainer()
    plots = bch.ResultReference(units="int")

    def __call__(self, **kwargs: Any) -> Any:
        self.update_params_from_kwargs(**kwargs)

        bench = bch.Bench("benchable", BenchableObject(), run_cfg=bch.BenchRunCfg(level=3))

        # if self.float_vars==0:

        inputs_vars_float = [
            BenchableObject.param.float1,
            BenchableObject.param.float2,
            BenchableObject.param.float3,
        ]

        # input_vars = inputs_vars_float[0 : self.float_vars]

        if self.float_vars == 1:
            input_vars = [BenchableObject.param.float1]
        elif self.float_vars == 2:
            input_vars = [BenchableObject.param.float1, BenchableObject.param.float2]
        else:
            input_vars = [
                BenchableObject.param.float1,
                BenchableObject.param.float2,
                BenchableObject.param.float3,
            ]

        # res = bench.plot_sweep("test", input_vars=input_vars)

        res = bench.plot_sweep(
            "test",
            input_vars=input_vars,
            result_vars=[BenchableObject.param.result_var],
            plot=False,
        )

        # bench.report.append(res.to_curve())
        # bench.report.append(res.to_surface_hv())
        # bench.report.append(res.to_volume())

        self.plots = bch.ResultReference()
        self.plots.obj = pn.Row(res.to_auto(width=300, height=300))

        # print(self.plots.obj)

        # bench.report.append(self.plots)

        # bench.report.append(res.to_panes())

        # return bench
        # print(super().__call__())

        return super().__call__()


def bench_bench_bench():
    # BenchMeta().__call__(float_vars=2).report.show()

    # bch.HoloviewResult.set_default_opts(width=300,height=300)

    bench = bch.Bench("bench_meta", BenchMeta())

    res = bench.plot_sweep("lol", input_vars=[BenchMeta.param.float_vars], plot=False)

    bench.report.append(res.to_sweep_summary())
    bench.report.append(res.to_references())

    bench.report.show()


if __name__ == "__main__":
    bench_bench_bench()
    # BenchableObject
