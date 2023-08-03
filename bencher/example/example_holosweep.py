# THIS IS NOT A WORKING EXAMPLE YET

# pylint: disable=duplicate-code,unused-argument


import bencher as bch
import math
import random
import numpy as np
import panel as pn
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

    # noisy = bch.BoolSweep(default=True)

    fn_output = bch.ResultVar(units="v", doc="sin of theta with some noise")
    # out_cos = bch.ResultVar(units="v", doc="cos of theta with some noise")

    out_sum = bch.ResultVar(units="v", doc="The sum")

    def calc(self, plot=True, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)
        # if self.noisy:
        noise = 0.1
        # else:
        # noise = 0.0

        self.fn_output = self.compute_fn.call(self.phase + self.freq * self.theta) + random.uniform(
            0, noise
        )

        return self.get_results_values_as_dict(holomap=self.plot(plot))

    def plot(self, plot=True) -> hv.Points:
        if plot:
            pt = hv.Text(0, 0, f"{self.phase}\n{self.freq}\n {self.theta}")
            pt *= hv.Ellipse(0, 0, 1)
            pt = hv.Points([self.theta, self.fn_output])
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


if __name__ == "__main__":
    # opts.defaults(
    #     # opts.NdLayout(shared_axes=False, shared_datasource=False, width=500),
    #     opts.Overlay(width=500, legend_position="right"),
    # )

    run_cfg = bch.BenchRunCfg()
    run_cfg.use_sample_cache = True
    run_cfg.only_hash_tag = True
    # run_cfg.auto_plot = False

    wv = PlotFunctions()
    bch_wv = bch.Bench("waves", wv.calc, plot_lib=None)

    # bch_wv.clear_tag_from_cache("")
    res = bch_wv.plot_sweep(
        "phase",
        input_vars=[wv.param.theta, wv.param.freq, wv.param.phase],
        result_vars=[wv.param.fn_output],
        run_cfg=run_cfg,
    )
    # hv.extension("matplotlib")
    bch_wv.append(res.to_grid())
    # bch_wv.append(hv.output(res.to_grid(), holomap="gif"))

    # bch_wv.append(hv.output(res.to_grid(), holomap="gif"))

    # bch_wv.append_tab(wv.to_dynamic_map(wv.calc))

    # bch_wv.worker = wv.calc_vec
    # res = bch_wv.plot_sweep(
    #     "holo",
    #     input_vars=[wv.param.freq, wv.param.phase, wv.param.compute_fn],
    #     result_vars=[wv.param.out_sum],
    #     run_cfg=run_cfg,
    # )

    # # # bch_wv.append_tab(res.to_heatmap())
    # bch_wv.append_tab(res.to_nd_layout())
    # bch_wv.append_tab(res.to_grid())
    # bch_wv.append_tab(wv.to_dynamic_map(wv.calc_vec))

    # bch_wv.append_tab(res.to_nd_layout())  # doesn't work on the same page yet.. TODO

    # bch_wv.append(res.to_grid())

    # bch_wv.append_tab(wv.to_dynamic_map(wv.calc_vec, "theta"))

    # bch_wv.append_tab(wv.to_holomap(wv.calc_vec, "theta"))

    # bch_wv.append(hv.HoloMap(res.hmap, res.hmap_kdims).opts(backend="bokeh"))
    # bch_wv.plots_instance.append(res.to_grid().opts(backend="bokeh"))
    # bch_wv.append(res.to_holomap().layout().)

    # bch_wv.append(res.to_holomap())
    # bch_wv.append(res.to_grid())

    # bch_wv.append(ndlay.grid("freq"))
    bch_wv.plot()

    # bch_wv.append(res.to_curve().layout())

    # res = bch_wv.plot_sweep(
    #     "phase",
    #     input_vars=[wv.param.theta, wv.param.freq, wv.param.phase, wv.param.noisy],
    #     # input_vars=[wv.param.theta, wv.param.freq, wv.param.phase],
    #     result_vars=[wv.param.fn_output],
    #     run_cfg=bch.BenchRunCfg(repeats=5),
    # )

    # bch_wv.plots_instance.append(res.to_curve())
    # bch_wv.plots_instance.append(res.to_curve().overlay("phase"))
    # bch_wv.plots_instance.append(res.to_curve().overlay("freq"))
    # bch_wv.plots_instance.append(res.to_curve().overlay("phase").layout())
    # bch_wv.plots_instance.append(res.to_curve().overlay("freq").layout())
    # bch_wv.plots_instance.append(res.to_curve().layout("phase"))
    # bch_wv.append(res.to_curve().overlay("phase"))
    gspec = pn.GridSpec()

    c1 = res.to_curve()  #
    c1 += res.to_curve().overlay("phase")
    # c1 += res.to_curve().overlay("freq")
    bch_wv.append(c1)
    # gspec[0, 0] = res.to_curve()
    # gspec[0, 1] = res.to_curve().overlay("phase")
    # gspec[1, 0] = res.to_curve().overlay("freq")

    bch_wv.append(gspec)

    # bch_wv.append(res.to_curve().layout("phase"))

    # bch_wv.append(res.to_curve().layout("freq"))
    # bch_wv.append(res.to_curve().layout())

    bch_wv.plot()


# todo  https://discourse.holoviz.org/t/pointdraw-as-parameterized-class/3539
