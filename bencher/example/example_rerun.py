import bencher as bch
import numpy as np
import rerun as rr
import rerun.blueprint as rrb


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



rr.init("rerun_example_my_blueprint",spawn=True)
# rr.send_blueprint(my_blueprint, make_active=True)
rr.log("lol1", rr.Points2D([0, 1]))
rr.log("lol2", rr.Points2D([1, 1]))

