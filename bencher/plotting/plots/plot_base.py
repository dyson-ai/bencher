# from bencher import Pa#
import param


from holoviews import opts
import holoviews as hv

hv.extension("bokeh", "plotly")

width_heigh = {"width": 600, "height": 600, "tools": ["hover"]}

opts.defaults(
    opts.Curve(**width_heigh),
    opts.Points(**width_heigh),
    opts.Bars(**width_heigh),
    opts.Scatter(**width_heigh),
    opts.HeatMap(cmap="plasma", **width_heigh, colorbar=True),
    # opts.Surface(**width_heigh),
    opts.GridSpace(plot_size=400),
)


class PlotBase:
    def title(self, x: param.Parameter, y: param.Parameter, z: param.Parameter = None) -> str:
        if z is None:
            return f"{x.name} vs {y.name}"
        return f"{z.name} vs ({x.name} vs {y.name})"
