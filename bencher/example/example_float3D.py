# pylint: disable=duplicate-code

import numpy as np

import bencher as bch


class VolumeSample(bch.ParametrizedSweep):
    """A class to represent a 3D point in space."""

    x = bch.FloatSweep(
        default=0, bounds=[-1.0, 1.0], doc="x coordinate of the sample volume", samples=8
    )
    y = bch.FloatSweep(
        default=0, bounds=[-1.0, 1.0], doc="y coordinate of the sample volume", samples=9
    )
    z = bch.FloatSweep(
        default=0, bounds=[-1.0, 1.0], doc="z coordinate of the sample volume", samples=10
    )


class VolumeResult(bch.ParametrizedSweep):
    """A class to represent the properties of a volume sample."""

    value = bch.ResultVar("ul", doc="The scalar value of the 3D volume field")
    occupancy = bch.ResultVar(
        "occupied", doc="If the value is > 0.5 this point is considered occupied"
    )
    interesting = bch.ResultVar("ul", doc="A more interesting scalar field")
    interesting_vec = bch.ResultVec(3, "vec", doc="A vector field with an interesting shape")
    interesting_vec_and_occ = bch.ResultVec(
        3, "vec", doc="The same vector field but only showing values in a sphere of radius 0.5"
    )


def bench_fn(point: VolumeSample) -> VolumeResult:
    """This function takes a 3D point as input and returns distance of that point to the origin.

    Args:
        point (VolumeSample): Sample point

    Returns:
        VolumeResult: Value at that point
    """
    output = VolumeResult()
    output.value = np.linalg.norm(np.array([point.x, point.y, point.z]))  # distance to origin
    output.occupancy = float(output.value < 0.5)
    # from https://plotly.com/python/3d-volume-plots/
    output.interesting = np.sin(np.pi * point.x) * np.cos(np.pi * point.z) * np.sin(np.pi * point.y)
    output.interesting_vec = [
        np.sin(np.pi * point.x),
        np.cos(np.pi * point.z),
        np.sin(np.pi * point.y),
    ]

    if output.occupancy:
        output.interesting_vec_and_occ = output.interesting_vec
    else:
        output.interesting_vec_and_occ = [0, 0, 0]

    return output


def example_floats3D(run_cfg: bch.BenchRunCfg) -> bch.Bench:
    """Example of how to perform a 3D floating point parameter sweep

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """
    bench = bch.Bench("Bencher_Example_Floats", bench_fn, VolumeSample)

    bench.plot_sweep(
        input_vars=[VolumeSample.param.x, VolumeSample.param.y, VolumeSample.param.z],
        result_vars=[
            VolumeResult.param.value,
            VolumeResult.param.occupancy,
            VolumeResult.param.interesting,
        ],
        title="Float 3D Example",
        description="""This example shows how to sample 3 floating point variables and plot a volumetric representation of the results.  The benchmark function returns the distance to the origin""",
        post_description="Here you can see concentric shells as the value of the function increases with distance from the origin. The occupancy graph should show a sphere with radius=0.5",
        run_cfg=run_cfg,
    )

    bench.plot_sweep(
        input_vars=[VolumeSample.param.x, VolumeSample.param.y, VolumeSample.param.z],
        result_vars=[
            VolumeResult.param.interesting_vec,
            VolumeResult.param.interesting_vec_and_occ,
        ],
        title="Float 3D Cone Example",
        description="""This example shows how to sample 3 floating point variables and plot a 3D vector field of the results.""",
        run_cfg=run_cfg,
    )

    return bench


if __name__ == "__main__":
    ex_run_cfg = bch.BenchRunCfg()
    example_floats3D(ex_run_cfg).plot()
