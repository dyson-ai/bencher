# from bencher import Pa#
import param
import xarray


from holoviews import opts
import holoviews as hv

hv.extension("bokeh", "plotly")

width_heigh = {"width": 600, "height": 600}

opts.defaults(
    opts.Curve(**width_heigh),
    opts.Points(**width_heigh),
    opts.Bars(**width_heigh),
    opts.Scatter(**width_heigh),
    # opts.Surface(**width_heigh),
)


class PlotBase:
    def title(self, x: param.Parameter, y: param.Parameter, z: param.Parameter = None) -> str:
        if z is None:
            return f"{x.name} vs {y.name}"
        return f"{z.name} vs ({x.name} vs {y.name})"

    def calculate_stats(self, da, over_dim="repeat"):
        mean = da.mean(over_dim)
        std = da.std(over_dim)

        low = mean + std
        high = mean - std
        mean = mean.rename("mean")
        low = low.rename("std_low")
        high = high.rename("std_high")

        return xarray.merge([mean, low, high]), std
