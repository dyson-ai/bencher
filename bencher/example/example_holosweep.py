# THIS IS NOT A WORKING EXAMPLE YET

# pylint: disable=duplicate-code,unused-argument


import bencher as bch
import holoviews as hv
import math
import panel as pn


class InteractiveExplorer(bch.ParametrizedSweep):
    ###INPUTS
    theta = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=30
    )
    offset = bch.FloatSweep(default=0, bounds=[0, 0.3], doc="dc offset", units="v", samples=30)
    # noisy = bch.BoolSweep(
    #     default=False, doc="Optionally add random noise to the output of the function"
    # )

    # noise_distribution = bch.EnumSweep(NoiseDistribution, doc=NoiseDistribution.__doc__)

    sigma = bch.FloatSweep(
        default=1,
        bounds=[0, 10],
        doc="The standard deviation of the noise",
        units="v",
    )

    # RESULTS

    out_sin = bch.ResultVar(
        units="v", direction=bch.OptDir.minimize, doc="sin of theta with some noise"
    )
    out_cos = bch.ResultVar(
        units="v", direction=bch.OptDir.minimize, doc="cos of theta with some noise"
    )

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)

        noise = 0.0

        self.out_sin = self.offset + math.sin(self.theta) + noise
        self.out_cos = self.offset + math.cos(self.theta) + noise

        # print(self.theta)

        return self.get_results_values_as_dict()

    def plot_hv(self, *args, **kwargs):
        # print("plotting")
        origin = [0, 0]
        res = [self.out_sin, self.out_cos]
        points = [origin, res]
        return hv.Points(points) * hv.Curve(points)

    def call_and_plot(self, **kwargs):
        self.__call__(**kwargs)
        return self.plot_hv()


if __name__ == "__main__":
    explorer = InteractiveExplorer()

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

    dmap = hv.DynamicMap(explorer.call_and_plot, kdims=explorer.get_inputs_as_dims())
    main.append(dmap)
    # main.append(dmap.)

    # plot_fn = hv.DynamicMap(explorer.plot_model)

    # main = pn.Row(
    #     pn.Column(*bch.get_inputs_only(explorer)),
    #     plot_fn,
    #     name="StickMan Interactive",
    # )

    main.show()

    # ex_run_cfg = bch.BenchRunCfg()

    # example_floats(ex_run_cfg).plot()
