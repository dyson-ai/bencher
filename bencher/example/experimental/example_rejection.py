from __future__ import annotations

import bencher as bch
import numpy as np
import holoviews as hv
from numpy.random import uniform, randint
from dataclasses import dataclass
from copy import deepcopy

from bencher.example.experimental.constrained_plotter import Stylus, Point

from enum import auto
from strenum import StrEnum


class Condition(StrEnum):
    control = auto()
    diseased = auto()


class Slopes(bch.ParametrizedSweep):
    # INPUTS
    condition = bch.EnumSweep(Condition)
    start_y = bch.box("start_y", 25, 4)

    adp_nmol = bch.IntSweep(default=27, bounds=[25, 30])
    x_delta3 = bch.FloatSweep(default=1, bounds=[1, 20])

    # RESULTS
    hmap = bch.ResultHmap()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)

        s = Stylus(Point(0, self.start_y))

        s.add_pt_with_grad(6, -0.16)
        s.add_pt_with_grad(self.x_delta3, -1, gradient_range=0.5)

        oxygen_nmol = 750
        adp_nmol = randint(25, 30) * 10
        # adp_nmol = self.adp_nmol * 10

        target_po_range = uniform(1.58, 1.7)
        max_y = s.points[0].y
        oxygen_au = oxygen_nmol / max_y
        target_delta_y = (adp_nmol / target_po_range) * (1 / oxygen_au)

        match self.condition:
            case Condition.control:
                s.add_pt_with_grad_ratio(4, 6, 1)
                # s.add_pt_y_diff_with_grad(y_delta=target_delta_y, gradient=-1.8)
                s.add_pt_with_grad(x_delta=4, gradient=-2.6, gradient_range=1)

            case Condition.diseased:
                s.add_pt_with_grad_ratio(6, 1)
                s.add_pt_with_grad(4, -0.6, 1)

        po_ratio = adp_nmol / ((s.points[1].y - s.points[2].y) * oxygen_au)

        s.add_pt_with_grad(4, -0.12, 1)
        # s.add_abs_point(x=20)

        state3 = s.points[2].gradient(s.points[1])
        state4 = s.points[3].gradient(s.points[2])
        ratio = state3 / state4

        self.hmap = s.to_curve(self.validate(s))
        # self.curve *= hv.Text(**s.points[3].as_dict(),text=s.points[3].gradient(s.points[4]))
        self.hmap *= hv.Text(s.points[2].x, s.points[2].y, str(ratio))

        # self.hmap *= hv.Text(10, 10, "".join(["ADP (nmol) = ", str(adp_nmol)]))
        # self.hmap *= hv.Text(10, 11, "".join(["P:O ratio = ", str(po_ratio)]))
        # self.hmap *= hv.Text(10, 12, "".join(["Oxygen per au = ", str(oxygen_au)]))
        # self.hmap *= hv.Text(s.points[1].x, s.points[1].y, str(s.points[1].y))
        # self.hmap *= hv.Text(s.points[2].x + 8, s.points[2].y, str(round(s.points[2].y, 4)))
        # self.hmap *= hv.Text(10, 15, "".join(["O diff = ", str(s.points[1].y - s.points[2].y)]))

        table_elements = []

        def add_table(item, val):
            table_elements.append((item, val))

        add_table("ADP (nmol)", adp_nmol)
        add_table("P:O ratio", po_ratio)
        add_table("Oxygen per au", oxygen_au)
        add_table("O diff", s.points[1].y - s.points[2].y)

        self.hmap += hv.ItemTable(table_elements)

        return super().__call__()

    def validate(self, plot: Stylus) -> bool:
        grad = plot.points[-1].gradient(plot.points[0])
        print(grad)
        return grad < -1.5


# vector(x_pos,y_pos,slope,time) = {x: round(slope * time + x_pos, 1), y: y_pos + time};

#     o.point = {};
#     o.point["1"] = {slope: 0.13333, time: 15, coords: {x: 0, y: 0+randomInt(0,10) }} ;
#     o.point["2"] = {slope: 0.48000, time: 12};
#     o.point["3"] = {slope: 1.70000+(randomInt(-5,5)/100), time: 10+randomInt(-1,2)};
#     o.point["4"] = {slope: o.point["3"].slope / (randomInt(53,74)/10), time: 10+randomInt(-1,2)};
#     o.point["5"] = {slope: 2.40000, time: 5+randomInt(-1,2)};
#     o.point["6"] = {slope: 0.40000, time: 10+randomInt(-1,2)};
#     o.point["7"] = {slope: 3.46667, time: 15+randomInt(-1,2)};
#     o.point["8"] = {slope: 0, time: 12+randomInt(-1,2)};
#     o.point["9"] = {};


run_cfg = bch.BenchRunCfg(repeats=5)
run_cfg.level = 6
bench = Slopes().to_bench(run_cfg)

Slopes().to_gui()


# bench.to_gui()


# res = bench.plot_sweep(input_vars=["condition"])
res = bench.plot_sweep(input_vars=["x_delta3"])


bench.report.append(res.to_holomap())

# res =bench.plot_sweep(input_vars=["adp_nmol"],plot=False)


# bench.report.append(res.to_holomap().layout(["condition"]))

# bench.report.append(res.to_holomap().overlay().opts(show_legend=False))
bench.report.show()
