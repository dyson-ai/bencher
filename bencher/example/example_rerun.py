import bencher as bch
import numpy as np
import rerun as rr
import rerun.blueprint as rrb
import panel as pn


my_blueprint = rrb.Blueprint(
    rrb.Horizontal(
        rrb.BarChartView(),
        rrb.Vertical(
            rrb.Spatial2DView(),
            rrb.Spatial3DView(),
        ),
    ),
)


# rr.init("rerun_example_my_blueprint", spawn=True, default_blueprint=my_blueprint)


rr.init(
    "rerun_example_my_blueprint",
    # spawn=True,
)


file_path = "dat.rrd"
rr.save(file_path)

# rr.send_blueprint(my_blueprint, make_active=True)
# rr.log("lol1", rr.Points2D([0, 1]))
# rr.log("lol2", rr.Points2D([1, 1]))
rr.log("s1", rr.Scalar(1))
rr.log("s1", rr.Scalar(2))
rr.log("s1", rr.Scalar(1))
rr.log("s1", rr.Scalar(2))


# exit()
bch.publish_and_view_rrd(
    file_path,
    remote="https://github.com/dyson-ai/bencher.git",
    branch_name="test_rrd",
    content_callback=bch.github_content,
).show()


