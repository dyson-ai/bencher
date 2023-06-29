from typing import Optional

import panel as pn
import plotly.express as px

from bencher.plotting.plot_filter import PlotFilter, PlotInput, VarRange
from bencher.plotting.plot_types import PlotTypes


class Plots2D:
    # shared plot filter for 2d plots
    plot_filter = PlotFilter(
        float_range=VarRange(2, 2),
        cat_range=VarRange(0, 0),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )

    def imshow(self, pl_in: PlotInput) -> Optional[pn.panel]:
        """use the imshow plotting method to display 2D data

        Args:
            pl_in (PlotInput): The data to plot

        Returns:
            List[pn.panel]: A panel with a image representation of the data
        """
        if self.plot_filter.matches(pl_in.plt_cnt_cfg):
            da = pl_in.bench_cfg.ds[pl_in.rv.name]
            mean = da.mean("repeat")
            fv_x = pl_in.plt_cnt_cfg.float_vars[0]
            fv_y = pl_in.plt_cnt_cfg.float_vars[1]
            title = f"{pl_in.rv.name} vs ({fv_x.name} vs {fv_y.name})"
            xlabel = f"{fv_x.name} [{fv_x.units}]"
            ylabel = f"{fv_y.name} [{fv_y.units}]"
            color_label = f"{pl_in.rv.name} [{pl_in.rv.units}]"
            return pn.panel(
                px.imshow(
                    mean,
                    title=title,
                    labels={"x": xlabel, "y": ylabel, "color": color_label},
                ),
                name=PlotTypes.heatmap_2D,
            )
        return None

    def heatmap_1D(self, pl_in: PlotInput) -> Optional[pn.panel]:
        """use the imshow plotting method to display a heatmap

        Args:
            pl_in (PlotInput): The data to plot

        Returns:
            List[pn.panel]: A panel with a image representation of the data
        """
        if PlotFilter(
            float_range=VarRange(0, 1),
            cat_range=VarRange(0, 1),
            vector_len=VarRange(1, 1),
            result_vars=VarRange(1, 1),
        ).matches(pl_in.plt_cnt_cfg):
            da = pl_in.bench_cfg.ds[pl_in.rv.name]
            # mean = da.mean("repeat")
            mean = da
            # print(pl_in.plt_cnt_cfg.cat_vars)
            # print(pl_in.plt_cnt_cfg.float_vars)
            # print(mean)

            print(mean.to_dataframe().reset_index())

            fv_x = pl_in.bench_cfg.iv_repeats
            fv_y = pl_in.bench_cfg.input_vars[0]

            title = f"{pl_in.rv.name} vs ({fv_x.name} vs {fv_y.name})"
            xlabel = f"{fv_x.name} [{fv_x.units}]"
            ylabel = f"{fv_y.name} [{fv_y.units}]"
            color_label = f"{pl_in.rv.name} [{pl_in.rv.units}]"
            return pn.panel(
                px.imshow(
                    mean,
                    title=title,
                    labels={"x": xlabel, "y": ylabel, "color": color_label},
                ),
                name=PlotTypes.heatmap_1D,
            )

            # print(mean.values)
            fv_x = pl_in.bench_cfg.input_vars[0]
            fv_x = pl_in.bench_cfg.input_vars[0]

            title = f"{pl_in.rv.name} vs {fv_x.name}"
            xlabel = f"{fv_x.name} [{fv_x.units}]"
            color_label = f"{pl_in.rv.name} [{pl_in.rv.units}]"
            return pn.panel(
                px.imshow(
                    [mean.values],
                    title=title,
                    labels={"x": xlabel, "y": ylabel, "color": color_label},
                ),
                name=PlotTypes.heatmap_1D,
            )
        return None
