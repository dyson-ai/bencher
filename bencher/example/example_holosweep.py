# THIS IS NOT A WORKING EXAMPLE YET

# pylint: disable=duplicate-code,unused-argument


import bencher as bch
import holoviews as hv
import math
import random
import numpy as np
from holoviews import opts


class InteractiveExplorer(bch.ParametrizedSweep):
    ###INPUTS
    theta = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=10
    )
    offset = bch.FloatSweep(default=0, bounds=[0, 0.3], doc="dc offset", units="v", samples=10)
    noisy = bch.BoolSweep(
        default=False, doc="Optionally add random noise to the output of the function"
    )

    phase = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=10
    )

    freq = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=10
    )

    # noise_distribution = bch.EnumSweep(NoiseDistribution, doc=NoiseDistribution.__doc__)

    # sigma = bch.FloatSweep(
    #     default=1,
    #     bounds=[0, 10],
    #     doc="The standard deviation of the noise",
    #     units="v",
    # )

    # RESULTS

    out_sin = bch.ResultVar(
        units="v", direction=bch.OptDir.minimize, doc="sin of theta with some noise"
    )
    out_cos = bch.ResultVar(
        units="v", direction=bch.OptDir.minimize, doc="cos of theta with some noise"
    )

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)

        noise = random.uniform(0, 1)

        self.out_sin = self.offset + math.sin(self.theta) + noise
        self.out_cos = self.offset + math.cos(self.theta) + noise

        # print(self.theta)

        return self.get_results_values_as_dict()

    def plot_hv(self, *args, **kwargs):
        print("plotting")
        origin = [0, 0]
        res = (self.out_sin, self.out_cos)
        points = [origin, res]
        points = [res]
        # return hv.Points(points) * hv.Curve(points)
        return hv.Points(points)

    def call_and_plot(self, **kwargs):
        print(kwargs)
        self.__call__(**kwargs)
        return self.plot_hv()


class Waves(bch.ParametrizedSweep):
    phase = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=4
    )

    freq = bch.FloatSweep(default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=4)

    theta = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=20
    )

    noise = bch.FloatSweep(default=0.0, bounds=[0.0, 1.0], doc="noise", units="rad", samples=3)

    out_sin = bch.ResultVar(
        units="v", direction=bch.OptDir.minimize, doc="sin of theta with some noise"
    )

    out_cos = bch.ResultVar(
        units="v", direction=bch.OptDir.minimize, doc="sin of theta with some noise"
    )

    # https://holoviews.org/reference/containers/bokeh/GridSpace.html
    def sine_curve(self, phase=0.0, freq=1.0, theta=0.0) -> hv.Points:
        print(f"phase:{phase} freq:{freq}")
        # return hv.Points([(phase, freq)]) * hv.Text(phase, freq, f"{phase},{freq}")
        xvals = [0.1 * i for i in range(100)]

        return hv.Curve((xvals, [np.sin(phase + freq * x) for x in xvals]))

    # https://holoviews.org/reference/containers/bokeh/GridSpace.html
    def calc(self, phase=0.0, freq=1.0, theta=0.0, noise=0.0):
        self.out_sin = np.sin(phase + freq * theta) + random.uniform(0, noise)
        self.out_cos = np.cos(phase + freq * theta) + random.uniform(0, noise)
        return self.get_results_values_as_dict()


if __name__ == "__main__":
    opts.defaults(
        # opts.GridSpace(shared_xaxis=True, shared_yaxis=True),
        opts.GridSpace(shared_xaxis=False, shared_yaxis=False, width=500),
        opts.NdLayout(shared_axes=False, shared_datasource=False, width=500),
        opts.Overlay(width=500, legend_position="right", show_legend=False),
        opts.Curve(width=500),
        opts.Spread(alpha=0.2),
    )
    wv = Waves()

    bch_wv = bch.Bench("waves", wv.calc, plot_lib=bch.PlotLibrary.default().add("lineplot_hv"))

    res = bch_wv.plot_sweep(
        "phase",
        input_vars=[wv.param.theta, wv.param.freq, wv.param.phase],
        const_vars=[(wv.param.noise, 1.0)],
        result_vars=[wv.param.out_sin],
        run_cfg=bch.BenchRunCfg(repeats=5),
    )

    bch_wv.plots_instance.append(res.to_curve())
    bch_wv.plots_instance.append(res.to_curve().overlay("phase"))
    bch_wv.plots_instance.append(res.to_curve().overlay("freq"))
    bch_wv.plots_instance.append(res.to_curve().overlay("phase").layout())
    bch_wv.plots_instance.append(res.to_curve().overlay("freq").layout())
    bch_wv.plots_instance.append(res.to_curve().layout("phase"))
    bch_wv.plots_instance.append(res.to_curve().layout("freq"))
    bch_wv.plots_instance.append(res.to_curve().layout())

    bch_wv.plot()
