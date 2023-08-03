# THIS IS NOT A WORKING EXAMPLE YET

# pylint: disable=duplicate-code,unused-argument


import bencher as bch
import math
import random
import numpy as np
import holoviews as hv

from strenum import StrEnum
from enum import auto


class Function(StrEnum):
    fn_cos = auto()
    fn_sin = auto()
    fn_log = auto()
    fn_arctan = auto()

    def call(self, arg) -> float:
        """Calls the function defined by the name of the enum

        Returns:
            float: The result of calling the function defined by the enum
        """
        return getattr(np, self.removeprefix("fn_"))(arg)


class PlotFunctions(bch.ParametrizedSweep):
    phase = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=5
    )

    freq = bch.FloatSweep(default=1, bounds=[0, math.pi], doc="Input angle", units="rad", samples=5)

    theta = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=10
    )

    compute_fn = bch.EnumSweep(Function)

    fn_output = bch.ResultVar(units="v", doc="sin of theta with some noise")

    out_sum = bch.ResultVar(units="v", doc="The sum")

    def calc(self, plot=True, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)
        noise = 0.1

        self.fn_output = self.compute_fn.call(self.phase + self.freq * self.theta) + random.uniform(
            0, noise
        )

        return self.get_results_values_as_dict(holomap=self.plot_holo(plot))

    def plot_holo(self, plot=True) -> hv.core.ViewableElement:
        """Plots a generic representation of the object that is not a basic hv datatype. In this case its an image of the values of the object, but it could be any representation of the object, e.g. a screenshot of the object state"""
        if plot:
            pt = hv.Text(0, 0, f"{self.phase}\n{self.freq}\n {self.theta}")
            pt *= hv.Ellipse(0, 0, 1)
            return pt
        return None

    def calc_vec(self, **kwargs) -> dict:
        theta = self.param.theta.values()
        kwargs.pop("theta", 0)
        dat = [self.calc(plot=False, theta=i, **kwargs)["fn_output"] for i in theta]
        # print(dat)
        self.out_sum = sum(dat)
        pt = hv.Curve((theta, dat), "theta", "voltage")
        # pt = hv.Text(0, 0, f"{self.compute_fn}\n{self.phase}\n{self.freq}")
        # pt *= hv.Ellipse(0, 0, 1)
        return self.get_results_values_as_dict(holomap=pt)


# from holoviews.selection import Ho


def example_holosweep_tap(run_cfg: bch.BenchRunCfg) -> bch.Bench:
    wv = PlotFunctions()
    bch_wv = bch.Bench("waves", wv.calc, plot_lib=None)

    # bch_wv.clear_tag_from_cache("")
    res = bch_wv.plot_sweep(
        "phase",
        input_vars=[wv.param.theta, wv.param.freq, wv.param.phase],
        result_vars=[wv.param.fn_output],
        run_cfg=run_cfg,
    )

    heatmap = res.to_heatmap().opts(tools=["hover", "tap"])
    posxy = hv.streams.Tap(source=heatmap, x=0, y=0)

    def tap_plot(x, y):
        print(x, y)

        selres = bch.get_nearest_coords(res.ds, theta=x, freq=y, phase=0, repeat=1)
        return res.hmap[bch.hmap_canonical_input(selres)]

    tap_dmap = hv.DynamicMap(tap_plot, streams=[posxy])

    bch_wv.append(heatmap + tap_dmap)

    bch_wv.append_tab(res.to_curve)
    return bch_wv


if __name__ == "__main__":
    example_holosweep_tap(bch.BenchRunCfg()).show()


# todo  https://discourse.holoviz.org/t/pointdraw-as-parameterized-class/3539