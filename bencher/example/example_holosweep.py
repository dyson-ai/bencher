# THIS IS NOT A WORKING EXAMPLE YET

# pylint: disable=duplicate-code,unused-argument


import bencher as bch
import math
import random
import numpy as np
from holoviews import opts


class Waves(bch.ParametrizedSweep):
    phase = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=4
    )

    freq = bch.FloatSweep(default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=4)

    theta = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=20
    )

    noisy = bch.BoolSweep(default=True)

    out_sin = bch.ResultVar(units="v", doc="sin of theta with some noise")
    out_cos = bch.ResultVar(units="v", doc="cos of theta with some noise")

    def calc(self, phase=0.0, freq=1.0, theta=0.0, noisy=True) -> dict:
        if noisy:
            noise = 1.0
        else:
            noise = 0.0

        self.out_sin = np.sin(phase + freq * theta) + random.uniform(0, noise)
        self.out_cos = np.cos(phase + freq * theta) + random.uniform(0, noise)
        return self.get_results_values_as_dict()


if __name__ == "__main__":
    opts.defaults(
        opts.NdLayout(shared_axes=False, shared_datasource=False, width=500),
        opts.Overlay(width=500, legend_position="right"),
    )
    wv = Waves()

    bch_wv = bch.Bench("waves", wv.calc)

    res = bch_wv.plot_sweep(
        "phase",
        # input_vars=[wv.param.theta, wv.param.freq, wv.param.phase, wv.param.noisy],
        input_vars=[wv.param.theta, wv.param.freq, wv.param.phase],
        result_vars=[wv.param.out_sin],
        run_cfg=bch.BenchRunCfg(repeats=5),
    )

    res = bch_wv.plot_sweep(
        "phase",
        # input_vars=[wv.param.theta, wv.param.freq, wv.param.phase, wv.param.noisy],
        input_vars=[wv.param.theta, wv.param.freq, wv.param.phase],
        result_vars=[wv.param.out_sin],
        run_cfg=bch.BenchRunCfg(repeats=5),
    )

    # bch_wv.plots_instance.append(res.to_curve())
    # bch_wv.plots_instance.append(res.to_curve().overlay("phase"))
    # bch_wv.plots_instance.append(res.to_curve().overlay("freq"))
    # bch_wv.plots_instance.append(res.to_curve().overlay("phase").layout())
    # bch_wv.plots_instance.append(res.to_curve().overlay("freq").layout())
    # bch_wv.plots_instance.append(res.to_curve().layout("phase"))
    bch_wv.plots_instance.append(res.to_curve().layout("freq"))
    bch_wv.plots_instance.append(res.to_curve().layout())

    bch_wv.plot()
