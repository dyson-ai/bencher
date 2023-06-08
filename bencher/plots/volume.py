
class PlotVolume(PlotSignature):
    def get_plot_signatures(self):
        plot_sig = PlotSignature()
        plot_sig.float_cnt = VarRange(2, 2)
        plot_sig.cat_range = VarRange(0, 0)
        plot_sig.vector_len = VarRange(2, 2)
        return plot_sig

    def plot_single(self, plot_sig: PlotSignature, bench_cfg: BenchCfg, rv: ResultVec):
        return self.plot_volume_plotly(bench_cfg, rv)

    def plot_volume_plotly(
        self, bench_cfg: BenchCfg, rv: ParametrizedOutput, xr_cfg: PltCfgBase
    ) -> pn.pane.Plotly:
        """Given a benchCfg generate a 3D surface plot

        Args:
            bench_cfg (BenchCfg): description of benchmark
            rv (ParametrizedOutput): result variable to plot
            xr_cfg (PltCfgBase): config of x,y variables

        Returns:
            pn.pane.Plotly: A 3d volume plot as a holoview in a pane
        """

        bench_cfg = wrap_long_time_labels(bench_cfg)

        da = bench_cfg.ds[rv.name]

        mean = da.mean("repeat")

        opacity = 0.1

        meandf = mean.to_dataframe().reset_index()

        data = [
            go.Volume(
                x=meandf[xr_cfg.x],
                y=meandf[xr_cfg.y],
                z=meandf[xr_cfg.z],
                value=meandf[rv.name],
                isomin=meandf[rv.name].min(),
                isomax=meandf[rv.name].max(),
                opacity=opacity,
                surface_count=20,
            )
        ]

        layout = go.Layout(
            title=f"{rv.name} vs ({xr_cfg.x} vs {xr_cfg.y} vs {xr_cfg.z})",
            autosize=True,
            width=700,
            height=700,
            margin=dict(t=50, b=50, r=50, l=50),
            scene=dict(
                xaxis_title=xr_cfg.xlabel,
                yaxis_title=xr_cfg.ylabel,
                zaxis_title=xr_cfg.zlabel,
            ),
        )

        fig = dict(data=data, layout=layout)

        return pn.pane.Plotly(fig)