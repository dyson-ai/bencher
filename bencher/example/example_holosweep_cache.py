# THIS IS NOT A WORKING EXAMPLE YET

# pylint: disable=duplicate-code,unused-argument


import bencher as bch
import math
import random
import numpy as np
import panel as pn
import holoviews as hv
import typing

from strenum import StrEnum
from enum import auto
import matplotlib


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

    # noisy = bch.BoolSweep(default=True)

    fn_output = bch.ResultVar(units="v", doc="sin of theta with some noise")

    out_sum = bch.ResultVar(units="v", doc="The sum")

    def calc(self, plot=True, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)
        print(f"calc with {kwargs}")
        noise = 0.1
        self.fn_output = self.compute_fn.call(self.phase + self.freq * self.theta) + random.uniform(
            0, noise
        )

        return self.get_results_values_as_dict(holomap=self.plot(plot))

    def plot(self, plot=True) -> hv.Points:
        if plot:
            pt = hv.Text(0, 0, f"{self.phase}\n{self.freq}\n {self.theta}")
            pt *= hv.Ellipse(0, 0, 1)
            pt *= hv.Points([self.theta, self.fn_output])
            pt *= hv.Polygons(
                [(0, 0), (0, 1), (1, 1), (1, 0)],
            ).opts(alpha=0.2, color="g")

            # hv.save(pt, "tmp.gif")
            # return hv.output(pt, filename="tmp.png", backend="matplotlib")
            # return hv.RGB.load_image("tmp.gif")
            return pt
        return None


if __name__ == "__main__":
    run_cfg = bch.BenchRunCfg()

    # hv.extension("matplotlib")
    # matplotlib.use("agg")
    run_cfg.use_sample_cache = True
    # run_cfg.only_hash_tag = True
    # run_cfg.auto_plot = False

    wv = PlotFunctions()
    bch_wv = bch.Bench("waves", wv.calc, plot_lib=None)

    bch_wv.clear_tag_from_cache("")
    res = bch_wv.plot_sweep(
        "phase",
        # input_vars=[wv.param.theta, wv.param.freq, wv.param.phase],
        input_vars=[wv.param.freq, wv.param.phase],
        result_vars=[wv.param.fn_output],
        run_cfg=run_cfg,
    )

    # res.to_holomap()
    # hv.extension("matplotlib")
    # bch_wv.append(res.to_holomap())

    hv.save(res.to_holomap(), "holomap.mp4")
    # bch_wv.append(res.to_nd_layout())
    bch_wv.append(hv.output(res.to_holomap(), holomap="mp4"))
    bch_wv.append(hv.output(res.to_holomap(), holomap="gif"))

    # hv.output(res.to_nd_layout(), filename="lol.mp4", backend="matplotlib")
    # hv.output(res.to_nd_layout(), filename="lol.png", backend="matplotlib")

    bch_wv.plot()
