import panel as pn
import plotly.graph_objs as go
from typing import Optional
import xarray as xr

from param import Parameter

from bencher.plotting.plot_filter import VarRange
from bencher.results.bench_result_base import BenchResultBase, ReduceType
from bencher.variables.results import ResultVar


class PlotlyResult(BenchResultBase):
    def to_volume(self, result_var: Parameter = None, **kwargs):
        return self.filter(
            self.to_volume_da,
            float_range=VarRange(3, 3),
            cat_range=VarRange(-1, 0),
            reduce=ReduceType.REDUCE,
            target_dimension=3,
            result_var=result_var,
            result_types=(ResultVar),
            **kwargs,
        )

    def to_volume_da(
        self, dataset: xr.Dataset, result_var: Parameter, width=600, height=600
    ) -> Optional[pn.pane.Plotly]:
        """Given a benchCfg generate a 3D surface plot
        Returns:
            pn.pane.Plotly: A 3d volume plot as a holoview in a pane
        """
        x = self.bench_cfg.input_vars[0]
        y = self.bench_cfg.input_vars[1]
        z = self.bench_cfg.input_vars[2]
        opacity = 0.1
        meandf = dataset[result_var.name].to_dataframe().reset_index()
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

        return pn.pane.Plotly(fig, name="volume_plotly")
