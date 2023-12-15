import panel as pn
import plotly.graph_objs as go

from bencher.plotting.plot_types import PlotTypes
from bencher.results.bench_result_base import BenchResultBase
from bencher.variables.parametrised_sweep import ParametrizedSweep


class PlotlyResult(BenchResultBase):
    def to_volume(self, result_var: ParametrizedSweep = None) -> pn.pane.Plotly:
        """Given a benchCfg generate a 3D surface plot
        Returns:
            pn.pane.Plotly: A 3d volume plot as a holoview in a pane
        """

        if result_var is None:
            result_var = self.bench_cfg.result_vars[0]

        x = self.bench_cfg.input_vars[0]
        y = self.bench_cfg.input_vars[1]
        z = self.bench_cfg.input_vars[2]
        width = 800
        height = 800

        da = self.to_dataarray(squeeze=False)
        mean = da.mean("repeat")

        opacity = 0.1

        meandf = mean.to_dataframe().reset_index()

        data = [
            go.Volume(
                x=meandf[x.name],
                y=meandf[y.name],
                z=meandf[z.name],
                value=meandf[result_var.name],
                isomin=meandf[result_var.name].min(),
                isomax=meandf[result_var.name].max(),
                opacity=opacity,
                surface_count=20,
            )
        ]

        layout = go.Layout(
            title=f"{result_var.name} vs ({x.name} vs {y.name} vs {z.name})",
            width=width,
            height=height,
            margin=dict(t=50, b=50, r=50, l=50),
            scene=dict(
                xaxis_title=f"{x.name} [{x.units}]",
                yaxis_title=f"{y.name} [{y.units}]",
                zaxis_title=f"{z.name} [{z.units}]",
            ),
        )

        fig = dict(data=data, layout=layout)

        return pn.pane.Plotly(fig, name=PlotTypes.volume_plotly)
