
class SurfacePlot(PlotSignature):
    def get_plot_signatures(self):
        plot_sig = PlotSignature()
        plot_sig.float_cnt = VarRange(2, 2)
        plot_sig.cat_range = VarRange(0, 0)
        plot_sig.vector_len = VarRange(2, 2)
        return plot_sig

    def plot_surface_plotly(
        self, bench_cfg: BenchCfg, rv: ParametrizedOutput, xr_cfg: PltCfgBase
    ) -> pn.pane.Plotly:
        """Given a benchCfg generate a 2D surface plot

        Args:
            bench_cfg (BenchCfg): description of benchmark
            rv (ParametrizedOutput): result variable to plot
            xr_cfg (PltCfgBase): config of x,y variables

        Returns:
            pn.pane.Plotly: A 2d surface plot as a holoview in a pane
        """

        if type(rv) == ResultVec:
            return plot_scatter3D_px(bench_cfg, rv)

        bench_cfg = wrap_long_time_labels(bench_cfg)

        da = bench_cfg.ds[rv.name].transpose()

        mean = da.mean("repeat")

        x = da.coords[xr_cfg.x]
        y = da.coords[xr_cfg.y]

        opacity = 0.3

        surfaces = [go.Surface(x=x, y=y, z=mean)]

        if bench_cfg.repeats > 1:
            std_dev = da.std("repeat")
            surfaces.append(
                go.Surface(x=x, y=y, z=mean + std_dev, showscale=False, opacity=opacity)
            )
            surfaces.append(
                go.Surface(x=x, y=y, z=mean - std_dev, showscale=False, opacity=opacity)
            )

        eye_dis = 1.7
        layout = go.Layout(
            title=xr_cfg.title,
            width=700,
            height=700,
            scene=dict(
                xaxis_title=xr_cfg.xlabel,
                yaxis_title=xr_cfg.ylabel,
                zaxis_title=xr_cfg.zlabel,
                camera=dict(eye=dict(x=eye_dis, y=eye_dis, z=eye_dis)),
            ),
        )

        fig = dict(data=surfaces, layout=layout)

        return pn.pane.Plotly(fig)

    def plot_surface_holo(
        self, bench_cfg: BenchCfg, rv: ParametrizedOutput, xr_cfg: PltCfgBase
    ) -> pn.pane.Plotly:
        """Given a benchCfg generate a 2D surface plot

        Args:
            bench_cfg (BenchCfg): description of benchmark
            rv (ParametrizedOutput): result variable to plot
            xr_cfg (PltCfgBase): config of x,y variables

        Returns:
            pn.pane.holoview: A 2d surface plot as a holoview in a pane
        """

        bench_cfg = wrap_long_time_labels(bench_cfg)

        alpha = 0.3

        da = bench_cfg.ds[rv.name]

        mean = da.mean("repeat")

        opts.defaults(
            opts.Surface(
                colorbar=True,
                width=800,
                height=800,
                zlabel=xr_cfg.zlabel,
                title=xr_cfg.title,
                # image_rtol=0.002,
            )
        )
        # TODO a warning suggests setting this parameter, but it does not seem to help as expected, leaving here to fix in the future
        # hv.config.image_rtol = 1.0

        ds = hv.Dataset(mean)
        surface = ds.to(hv.Surface)

        if bench_cfg.repeats > 1:
            std_dev = da.std("repeat")
            upper = hv.Dataset(mean + std_dev).to(hv.Surface).opts(alpha=alpha, colorbar=False)
            lower = hv.Dataset(mean - std_dev).to(hv.Surface).opts(alpha=alpha, colorbar=False)
            return surface * upper * lower
        else:
            return surface