import bencher as bch
import numpy as np
import holoviews as hv
from numpy.random import uniform


class Slopes(bch.ParametrizedSweep):
    condition = bch.StringSweep(["control", "diseased"])

    start_y = bch.box("start_y", 25, 4)
    slope1 = bch.box("slope1", -0.2, 0.1)
    slope2 = bch.box("slope2", -2, 0.2)
    slope3 = bch.box("slope3", -0.5, 0.2)
    slope4 = bch.box("slope4", -1, 0.3)
    slope5 = bch.box("slope5", -1.5, 0.4)

    curve = bch.ResultHmap()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        data = {}
        data[1] = {"slope": 0, "time": 0, "x": 0, "y": 25}
        data[2] = {"slope": -0.1667, "time": 6 + uniform(-1, 2)}
        data[3] = {"slope": -1.0000, "time": 3 + uniform(-1, 2)}

        if self.condition == "control":
            data[4] = {
                "slope": data[3]["slope"] / 6.0 + uniform(-0.1, 0.1),
                "time": 6 + uniform(-1, 2),
            }
            data[5] = {"slope": -2.6250, "time": 4 + uniform(-1, 2)}

        else:
            data[4] = {"slope": data[3]["slope"], "time": 6 + uniform(-1, 2)}
            data[5] = {"slope": -0.6250, "time": 4 + uniform(-1, 2)}

        # control[4] = {"slope": -0.1429 + uniform(-0.1, 0.1), "time": 6 + uniform(-1, 2)}
        data[6] = {"slope": -0.1250, "time": 4 + uniform(-1, 2)}

        def vector(t, slope, x, y):
            return {"x": x + t, "y": y + t * slope}

        def fn(ind):
            data[ind] = vector(
                t=data[ind]["time"],
                slope=data[ind]["slope"],
                x=data[ind - 1]["x"],
                y=data[ind - 1]["y"],
            )

        [fn(i) for i in range(2, 6)]

        ou = [((data[i]["x"], data[i]["y"])) for i in range(1, 6)]
        self.curve = hv.Curve(ou)
        return super().__call__()


run_cfg = bch.BenchRunCfg(repeats=10)
bench = Slopes().to_bench(run_cfg)
res = bench.plot_sweep(input_vars=["condition"])

bench.report.append(res.to_holomap())
bench.report.append(res.to_holomap().layout(["condition"]))

bench.report.append(res.to_holomap().overlay().opts(show_legend=False))
bench.report.show()
