# THIS IS NOT A WORKING EXAMPLE YET

# pylint: disable=duplicate-code,unused-argument


import bencher as bch
import math
import random
import numpy as np
from holoviews import opts
import panel as pn
import holoviews as hv


class Waves(bch.ParametrizedSweep):
    phase = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=5
    )

    freq = bch.FloatSweep(default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=4)

    theta = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=10
    )

    noisy = bch.BoolSweep(default=True)

    out_sin = bch.ResultVar(units="v", doc="sin of theta with some noise")
    out_cos = bch.ResultVar(units="v", doc="cos of theta with some noise")

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

    def calc_vec(self, phase=0.0, freq=1.0, noisy=True) -> dict:
        if noisy:
            noise = 1.0
        else:
            noise = 0.0

        theta = np.arange(0, 6, 0.1)
        dat = np.sin(phase + freq * theta) + random.uniform(0, noise)

        self.out_sum = sum(dat)
        hmap = hv.Curve((theta, dat), "theta", "voltage")
        return self.get_results_values_as_dict(holomap=hmap)


if __name__ == "__main__":
    opts.defaults(
        # opts.NdLayout(shared_axes=False, shared_datasource=False, width=500),
        opts.Overlay(width=500, legend_position="right"),
    )
    wv = Waves()

    bch_wv = bch.Bench("waves", wv.calc, plot_lib=None)

    res = bch_wv.plot_sweep(
        "phase",
        # input_vars=[wv.param.theta, wv.param.freq, wv.param.phase, wv.param.noisy],
        input_vars=[wv.param.theta, wv.param.freq, wv.param.phase],
        result_vars=[wv.param.out_sin],
        run_cfg=bch.BenchRunCfg(repeats=3),
    )

    bch_wv.append(res.to_curve().layout("freq"))

    bch_wv.worker = wv.calc_vec
    res = bch_wv.plot_sweep(
        "holo",
        input_vars=[wv.param.freq, wv.param.phase],
        result_vars=[wv.param.out_sum],
        run_cfg=bch.BenchRunCfg(repeats=3),
    )

    bch_wv.append(res.to_holomap())

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
