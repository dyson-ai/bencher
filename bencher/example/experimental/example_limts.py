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


class Limits(bch.ParametrizedSweep):
    # INPUTS

    adp_nmol = bch.IntSweep(default=27, bounds=[25, 30])
    # target_po_range

    target_delta_y = bch.ResultVar()
    po = bch.ResultVar()

    hmap = bch.ResultHmap()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)

        oxygen_nmol = 1000
        # adp_nmol = randint(25, 30) * 10
        adp_nmol = self.adp_nmol * 10
        target_po_range = uniform(1.58, 1.7)
        max_y = 25
        oxygen_au = oxygen_nmol / max_y
        target_delta_y = (adp_nmol / target_po_range) * (1 / oxygen_au)

        # self.po =

        self.target_delta_y = target_delta_y

        self.hmap = hv.Points([0, self.target_delta_y])

        return super().__call__()


run_cfg = bch.BenchRunCfg()
run_cfg.repeats = 10

import panel as pn

row = pn.Row()

lim = Limits()

# dm = hv.DynamicMap(lim.__call__)

# return hv.DynamicMap(
    # callback=callback_wrapper,
    # kdims=self.get_inputs_as_dims(compute_values=False, remove_dims=remove_dims),
    # name=name,
# ).opts(shared_axes=False, framewise=True, width=1000, height=1000)

# row.append(dm)

row.show()

# Limits().to_gui()


bench = Limits().to_bench(run_cfg)

res = bench.plot_sweep("lol")

ds = res.to_dataset(reduce=None)

# bench.report.append(ds)


# bench.report.append(res.to_scatter_jitter_single(Slopes.param.res))
# bench.report.append(res.to_scatter_jitter())

# bench.report.append(res.to_holomap())
# bench.report.append(res.to_holomap().layout(["condition"]))
#
# bench.report.append(res.to_holomap().overlay().opts(show_legend=False))
bench.report.show()
