import bencher as bch
import rerun as rr
import rerun.blueprint as rrb

from bencher.rerun_utils import to_pane, rrd_to_pane

# my_blueprint = rrb.Blueprint(
#     rrb.Horizontal(
#         rrb.BarChartView(),
#         rrb.Vertical(
#             rrb.Spatial2DView(),
#             rrb.Spatial3DView(),
#         ),
#     ),
# )

rr.init("rerun_example_my_blueprint", spawn=True)


# file_path = "dat.rrd"
# rr.save(file_path)

# # rr.send_blueprint(my_blueprint, make_active=True)
# rr.log("s1", rr.Scalar(1))
# rr.log("s1", rr.Scalar(2))
# rr.log("s1", rr.Scalar(1))
# rr.log("s1", rr.Scalar(2))

# bch.publish_and_view_rrd(
#     file_path,
#     remote="https://github.com/dyson-ai/bencher.git",
#     branch_name="test_rrd",
#     content_callback=bch.github_content,
# ).show()


import math
import bencher as bch


class SweepRerun(bch.ParametrizedSweep):
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

    bench = SweepRerun().to_bench(run_cfg, report)
    bench.plot_sweep()
    return bench


if __name__ == "__main__":
    example_rerun(bch.BenchRunCfg(level=3)).report.show()
