# pylint: disable=duplicate-code

import numpy as np
import bencher as bch

class VolumeSample(bch.ParametrizedSweep):
    """A class to represent a 3D point in space."""

    x = bch.FloatSweep(
        default=0, bounds=[-1.0, 1.0], doc="x coordinate of the sample volume", samples=2
    )
    y = bch.FloatSweep(
        default=0, bounds=[-1.0, 1.0], doc="y coordinate of the sample volume", samples=3
    )
    z = bch.FloatSweep(
        default=0, bounds=[-1.0, 1.0], doc="z coordinate of the sample volume", samples=4
    )


    value = bch.ResultVar("ul", doc="The scalar value of the 3D volume field")   
    interesting = bch.ResultVar("ul", doc="A more interesting scalar field")

    def __call__(self,**kwargs):
        self.update_params_from_kwargs(**kwargs)
        self.value = np.linalg.norm(np.array([self.x, self.y, self.z]))  # distance to origin
        self.interesting = np.sin(np.pi * self.x) * np.cos(np.pi * self.z) * np.sin(np.pi * self.y)

        # self.interesting_vec = [
        #     np.sin(np.pi * point.x),
        #     np.cos(np.pi * point.z),
        #     np.sin(np.pi * point.y),
        # ]
        return self.get_results_values_as_dict()

    def call_tensor(self,**kwargs):
        pass



def example_floats3D(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    """Example of how to perform a 3D floating point parameter sweep

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """
    bench = bch.Bench(
        "Bencher_Example_Tensor",
        VolumeSample(),
        # plot_lib=bch.PlotLibrary.with_plotly(),
        run_cfg=run_cfg,
        report=report,
    )

    res = bench.plot_sweep(
        title="Float 3D Example",
        input_vars=[VolumeSample.param.x, VolumeSample.param.y],
        result_vars=[
            VolumeSample.param.value,
            VolumeSample.param.interesting
        ],
        description="""This example shows how to sample 3 floating point variables and plot a volumetric representation of the results.  The benchmark function returns the distance to the origin""",
        post_description="Here you can see concentric shells as the value of the function increases with distance from the origin. The occupancy graph should show a sphere with radius=0.5",
    )

    # bench.report.append(res.to_volume())
    
    return bench


if __name__ == "__main__":
    ex_run_cfg = bch.BenchRunCfg()
    example_floats3D(ex_run_cfg).report.show()
