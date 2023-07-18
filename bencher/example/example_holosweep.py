# THIS IS NOT A WORKING EXAMPLE YET

# pylint: disable=duplicate-code,unused-argument


import bencher as bch
import holoviews as hv
import math
import panel as pn
import random
import numpy as np


class InteractiveExplorer(bch.ParametrizedSweep):
    ###INPUTS
    theta = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=10
    )
    offset = bch.FloatSweep(default=0, bounds=[0, 0.3], doc="dc offset", units="v", samples=10)
    noisy = bch.BoolSweep(
        default=False, doc="Optionally add random noise to the output of the function"
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
        res = [self.out_sin, self.out_cos]
        points = [origin, res]
        # return hv.Points(points) * hv.Curve(points)
        return hv.Points(points)

    def call_and_plot(self, **kwargs):
        print(kwargs)
        self.__call__(**kwargs)
        return self.plot_hv()


# https://holoviews.org/reference/containers/bokeh/GridSpace.html
def sine_curve(phase, freq):
    xvals = [0.1 * i for i in range(100)]
    return hv.Curve((xvals, [np.sin(phase + freq * x) for x in xvals]))


if __name__ == "__main__":
    phases = [0, np.pi / 2, np.pi, 3 * np.pi / 2]
    frequencies = [0.5, 0.75, 1.0, 1.25]
    curve_dict_2D = {(p, f): sine_curve(p, f) for p in phases for f in frequencies}

    gridspace = hv.GridSpace(curve_dict_2D, kdims=["phase", "frequency"])
    hv.output(size=50)
    hmap = hv.HoloMap(gridspace)
    hmap += hv.GridSpace(hmap)

    mn = pn.Row()
    mn.append(hmap)

    mn.show()

    explorer = InteractiveExplorer()

    bencher = bch.Bench("holoviews", explorer.__call__)

    res = bencher.plot_sweep(
        "holosweep",
        [explorer.param.theta, explorer.param.offset],
        [explorer.param.out_sin],
        run_cfg=bch.BenchRunCfg(repeats=10),
    )

    # res = bencher.plot_sweep(
    #     "holosweep",
    #     [explorer.param.theta],
    #     [explorer.param.out_sin],
    #     run_cfg=bch.BenchRunCfg(repeats=10),
    # )

    ds = hv.Dataset(res.ds)
    from holoviews import opts

    opts.defaults(
        # opts.GridSpace(shared_xaxis=True, shared_yaxis=True),
        opts.GridSpace(shared_xaxis=False, shared_yaxis=False),
        opts.Image(shared_axes=False),
        # opts.Image(cmap="viridis", width=400, height=400),
        opts.Labels(
            text_color="white", text_font_size="8pt", text_align="left", text_baseline="bottom"
        ),
        opts.Path(color="white"),
        opts.Spread(width=600),
        opts.Overlay(show_legend=False),
    )
    print(ds.kdims)
    print(ds.vdims)
    print(ds)

    print(res.ds)

    iv = [v.name for v in res.input_vars]
    rv = [r.name for r in res.result_vars]
    # hv.Dataset.aggregate()
    ds_red = ds.reduce(["repeat"], np.mean, np.std)
    ds_agg = ds.aggregate(iv, np.mean, np.std)
    # ds_agg_rv = ds.aggregate(rv, np.mean, np.std)

    # ds_agg.

    bencher.get_panel().append(ds.to(hv.Table))
    bencher.get_panel().append(ds_red.to(hv.Table))
    bencher.get_panel().append(ds_agg.to(hv.Table))
    # bencher.get_panel().append(ds_agg_rv.to(hv.Table))

    if len(iv) == 2:
        bencher.get_panel().append(ds.to(hv.Image))
        bencher.get_panel().append(ds_red.to(hv.Image))
        bencher.get_panel().append(ds_agg.to(hv.Image))

    bencher.get_panel().append(ds_red.to(hv.Curve))

    bencher.get_panel().append(ds_agg.to(hv.Curve).grid())

    # bencher.get_panel().append(ds_agg.to(hv.Curve).grid("offset").opts(height=200))
    # bencher.get_panel().append(ds_agg.to(hv.Curve, "theta").grid("offset"))

    # bencher.get_panel().append(hv.Curve(ds, kdims=["theta", "offset"], vdims=["out_sin"]))

    bencher.get_panel().append(ds_agg.to(hv.Curve) * ds_agg.to(hv.Spread).opts(alpha=0.2))
    bencher.get_panel().append(ds_agg.to(hv.Curve).grid() * ds_agg.to(hv.Spread).grid())

    # bencher.get_panel().append(
    #     hv.Curve(ds).reduce(["repeat"]) * hv.Spread(ds).reduce(["repeat"]).opts(alpha=0.2)
    # )
    bencher.get_panel().append(hv.Curve(ds_agg) * hv.Spread(ds_agg).opts(alpha=0.2))

    bencher.plot()

    main = pn.Column()

    # curv_dict = explorer.

    # for inp in explorer.get_inputs_only():
    #     fslider = pn.widgets.FloatSlider(name=inp.name, start=inp.bounds[0], end=inp.bounds[1])
    #     s_bind = pn.bind(explorer.__call__, theta=fslider)
    #     main.append(
    #         pn.Row(
    #             f"# {inp.name}",
    #             fslider,
    #             s_bind,
    #             pn.widgets.EditableRangeSlider(
    #                 name=inp.name,
    #                 start=inp.bounds[0],
    #                 end=inp.bounds[1],
    #             ),
    #             pn.widgets.Checkbox(),
    #         )
    #     )

    # bt = pn.widgets.Button()
    # bt_bn = pn.bind(explorer.plot_hv, bt)

    # main.append(bt)
    # main.append(bt_bn)
    # print(explorer.get_inputs_as_dims())

    dmap = hv.DynamicMap(explorer.call_and_plot, kdims=explorer.get_inputs_as_dims())

    ds = dmap.apply(hv.Dataset)

    print(ds)

    hmap = hv.DynamicMap(explorer.call_and_plot, kdims=explorer.get_inputs_as_dims(True))
    main.append(dmap)
    # main.append(hmap)
    main.append(ds.to(hv.Point, "theta").grid())
    # main.append(ds.to(hv.Point,"theta").grid("theta"))
    # main.append(hmap.overlay("theta").grid("offset"))
    # main.append(hmap.grid("theta"))

    # plot_fn = hv.DynamicMap(explorer.plot_model)

    # main = pn.Row(
    #     pn.Column(*bch.get_inputs_only(explorer)),
    #     plot_fn,
    #     name="StickMan Interactive",
    # )

    main.show()

    # ex_run_cfg = bch.BenchRunCfg()

    # example_floats(ex_run_cfg).plot()
