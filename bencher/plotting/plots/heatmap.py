from typing import Optional

import panel as pn
import plotly.express as px
import xarray as xr

import hvplot.xarray  # noqa pylint: disable=unused-import


from bencher.bench_vars import ParametrizedSweep
from bencher.plotting.plot_filter import PlotFilter, PlotInput, VarRange
from bencher.plotting.plot_types import PlotTypes


class Heatmap:
    # shared plot filter for 2d plots
    plot_filter = PlotFilter(
        float_range=VarRange(2, 2),
        cat_range=VarRange(0, 0),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )

    def imshow_wrapper(
        self,
        df: xr.DataArray,
        x: ParametrizedSweep,
        y: ParametrizedSweep,
        z: ParametrizedSweep,
        name: str,
    ) -> pn.panel:
        """given a dataframe and result variables, use imshow to plot a heatmap

        Args:
            df (xr.DataArray): data to plot
            x (ParametrizedSweep): x variable
            y (ParametrizedSweep): y variable
            z (ParametrizedSweep): z variable
            name (str): name of the plot

        Returns:
            pn.panel: A heatmap
        """
        title = f"{z.name} vs ({x.name} vs {y.name})"
        xlabel = f"{x.name} [{x.units}]"
        ylabel = f"{y.name} [{y.units}]"
        color_label = f"{z.name} [{z.units}]"

        # TODO set up a holoview version
        # return pn.panel(df.hvplot.heatmap(x=x.name, y=y.name, C=z.name, colorbar=True))
        return pn.panel(
            px.imshow(
                df,
                title=title,
                labels={"x": xlabel, "y": ylabel, "color": color_label},
            ),
            name=name,
        )

    def heatmap_2D(self, pl_in: PlotInput) -> Optional[pn.panel]:
        """use the imshow plotting method to display 2D data

        Args:
            pl_in (PlotInput): The data to plot

        Returns:
            pn.panel: A panel with a image representation of the data
        """
        if len(pl_in.bench_cfg.input_vars) == 2:
            da = pl_in.bench_cfg.ds[pl_in.rv.name]
            mean = da.mean("repeat")

            x = pl_in.bench_cfg.input_vars[0]
            y = pl_in.bench_cfg.input_vars[1]
            z = pl_in.rv

            title = f"{z.name} vs ({x.name} vs {y.name})"
            color_label = f"{z.name} [{z.units}]"

            return pn.panel(
                mean.hvplot.heatmap(
                    x=x.name,
                    y=y.name,
                    C=z.name,
                    title=title,
                    label=pl_in.rv.name,
                    colorbar=True,
                    clabel=color_label,
                ),
                name=PlotTypes.heatmap_2D,
            )
        return None

    def heatmap_1D(self, pl_in: PlotInput) -> Optional[pn.panel]:
        """use the imshow plotting method to display a heatmap

        Args:
            pl_in (PlotInput): The data to plot

        Returns:
            Optional[pn.panel]: A panel with a image representation of the data
        """
        if len(pl_in.bench_cfg.input_vars) == 1:
            da = pl_in.bench_cfg.ds[pl_in.rv.name]
            mean = da.mean("repeat", keepdims=True, keep_attrs=True)

            return [
                self.imshow_wrapper(
                    da,
                    pl_in.bench_cfg.iv_repeat,
                    pl_in.bench_cfg.input_vars[0],
                    pl_in.rv,
                    PlotTypes.heatmap_2D,
                ),
                self.imshow_wrapper(
                    mean,
                    pl_in.bench_cfg.iv_repeat,
                    pl_in.bench_cfg.input_vars[0],
                    pl_in.rv,
                    PlotTypes.heatmap_1D,
                ),
            ]
        return None
