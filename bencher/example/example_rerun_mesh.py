import bencher as bch
import rerun as rr
import rerun.blueprint as rrb
import open3d as o3d
from bencher.utils_rerun import to_pane, rrd_to_pane

from bencher.variables.rerun_result import ResultRerunData

import math
import bencher as bch

rr.init("rerun_example_my_blueprint", spawn=True)

class PoissonParams(bch.ParametrizedSweep):
    depth = bch.IntSweep(default=7, bounds=[7, 10])
    # widdepth = bch.IntSweep(default=7,bounds=[7,10])
    # width: Final = [0.0, 5.0, 10.0, 15.0]
    # scale: Final = [1.0, 1.1, 1.2, 1.3, 1.4]
    linear_fit = bch.BoolSweep()

    # def load_data(self, **params):
    def __init__(self, **params):
        super().__init__(*params)

        example_data = o3d.data.PCDPointCloud()  # Points to the example PLY file
        self.pcd = o3d.io.read_point_cloud(
            example_data.path
        )  # Load the point cloud from file
        print(f"Loaded point cloud has {len(self.pcd.points)} points.")
        # Estimate normals for the point cloud
        self.pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
        )
        self.pcd.orient_normals_consistent_tangent_plane(k=30)

    def __call__(self, **kwargs)->dict:
        self.update_params_from_kwargs(**kwargs)

        mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            self.pcd, depth=self.depth, width=0, scale=1.1, linear_fit=self.linear_fit
        )

        return super().__call__()  # returns dict of all class params


class SweepRerunMesh(bch.ParametrizedSweep):
    theta = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=30
    )

    out_pane = bch.ResultContainer()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        self.out_sin = math.sin(self.theta)

        self.out_pane = bch.record_rerun_session() 
        rr.log("s1", rr.Scalar(self.theta))
        rr.log("s1", rr.Scalar(self.theta + 1))

        return super().__call__(**kwargs)


def example_rerun(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:
    """This example shows how to sample a 1 dimensional float variable and plot the result of passing that parameter sweep to the benchmarking function"""

    bench = SweepRerunMesh().to_bench(run_cfg, report)
    bench.plot_sweep()
    return bench


if __name__ == "__main__":
    example_rerun(bch.BenchRunCfg(level=3)).report.show()
