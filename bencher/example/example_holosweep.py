# THIS IS NOT A WORKING EXAMPLE YET

# pylint: disable=duplicate-code,unused-argument


import bencher as bch
import math
import random
import numpy as np
from holoviews import opts
import panel as pn
import holoviews as hv


from strenum import StrEnum
from enum import auto


class Function(StrEnum):
    fn_cos = auto()
    fn_sin = auto()


class Waves(bch.ParametrizedSweep):
    phase = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=2
    )

    freq = bch.FloatSweep(default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=2)

    theta = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=10
    )

    compute_fn = bch.EnumSweep(Function)

    noisy = bch.BoolSweep(default=True)

    out_sin = bch.ResultVar(units="v", doc="sin of theta with some noise")
    # out_cos = bch.ResultVar(units="v", doc="cos of theta with some noise")

    out_sum = bch.ResultVar(units="v", doc="The sum")

    def calc(self, phase=0.0, freq=1.0, theta=0.0, noisy=True) -> dict:
        if noisy:
            noise = 1.0
        else:
            noise = 0.0

        self.out_sin = np.sin(phase + freq * theta) + random.uniform(0, noise)
        self.out_cos = np.cos(phase + freq * theta) + random.uniform(0, noise)

        # self.image = hv.Text

        pt = hv.Text(0, 0, f"{phase}\n{freq}\n {theta}")
        pt *= hv.Ellipse(0, 0, 1)
        pt = hv.Points([theta, self.out_sin])

        return self.get_results_values_as_dict(holomap=pt)

    def calc_vec(
        self, phase=0.0, freq=1.0, noisy=True, compute_fn: Function = Function.fn_sin
    ) -> dict:
        if noisy:
            noise = 1.0
        else:
            noise = 0.0

        theta = np.arange(0, 6, 0.1)

        match compute_fn:
            case Function.fn_sin:
                dat = np.sin(phase + freq * theta) + random.uniform(0, noise)
            case Function.fn_cos:
                dat = np.cos(phase + freq * theta) + random.uniform(0, noise)

        self.out_sum = sum(dat)
        hmap = hv.Curve((theta, dat), "theta", "voltage")

        pt = hv.Text(0, 0, f"{compute_fn}\n{phase}\n{freq}")
        pt *= hv.Ellipse(0, 0, 1)

        # pt = hv.Image(np.ones([100, 100]) * freq * phase * 100)
        # pt = hv.Points([theta, self.out_sin])

        return self.get_results_values_as_dict(holomap=pt)


if __name__ == "__main__":
    # opts.defaults(
    #     # opts.NdLayout(shared_axes=False, shared_datasource=False, width=500),
    #     opts.Overlay(width=500, legend_position="right"),
    # )
    wv = Waves()

    # hv.extension("plotly", "bokeh")

    bch_wv = bch.Bench("waves", wv.calc, plot_lib=None)

    # res = bch_wv.plot_sweep(
    #     "phase",
    #     # input_vars=[wv.param.theta, wv.param.freq, wv.param.phase, wv.param.noisy],
    #     input_vars=[wv.param.theta, wv.param.freq, wv.param.phase],
    #     result_vars=[wv.param.out_sin],
    #     run_cfg=bch.BenchRunCfg(repeats=3),
    # )

    # bch_wv.append(res.to_curve().layout("freq"))

    bch_wv.worker = wv.calc_vec
    res = bch_wv.plot_sweep(
        "holo",
        input_vars=[wv.param.freq, wv.param.phase, wv.param.compute_fn],
        result_vars=[wv.param.out_sum],
        run_cfg=bch.BenchRunCfg(repeats=3, auto_plot=False),
    )

    # hv.extension("bokeh")

    # bch_wv.append(res.to_holomap().opts(backend="bokeh"))

    # bch_wv.append(hv.HoloMap(res.hmap, res.hmap_kdims).opts(backend="bokeh"))
    # bch_wv.plots_instance.append(res.to_grid().opts(backend="bokeh"))
    # bch_wv.append(res.to_holomap().layout().)

    # bch_wv.append(res.to_holomap())
    bch_wv.append(res.to_grid())

    # bch_wv.append(ndlay.grid("freq"))
    bch_wv.plot()

    # bch_wv.append(res.to_curve().layout())

    # res = bch_wv.plot_sweep(
    #     "phase",
    #     input_vars=[wv.param.theta, wv.param.freq, wv.param.phase, wv.param.noisy],
    #     # input_vars=[wv.param.theta, wv.param.freq, wv.param.phase],
    #     result_vars=[wv.param.out_sin],
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
