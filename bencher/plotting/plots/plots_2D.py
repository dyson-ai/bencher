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

    def imshow_wrapper(self, df, x, y, z, name) -> pn.panel:
        title = f"{z.name} vs ({x.name} vs {y.name})"
        xlabel = f"{x.name} [{x.units}]"
        ylabel = f"{y.name} [{y.units}]"
        color_label = f"{z.name} [{z.units}]"
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
            List[pn.panel]: A panel with a image representation of the data
        """
        if len(pl_in.bench_cfg.input_vars) == 2:
            da = pl_in.bench_cfg.ds[pl_in.rv.name]
            mean = da.mean("repeat")

            return self.imshow_wrapper(
                mean,
                pl_in.bench_cfg.input_vars[0],
                pl_in.bench_cfg.input_vars[1],
                pl_in.rv,
                PlotTypes.heatmap_2D,
            )
        return None

    def heatmap_1D(self, pl_in: PlotInput) -> Optional[pn.panel]:
        """use the imshow plotting method to display a heatmap

        Args:
            pl_in (PlotInput): The data to plot

        Returns:
            List[pn.panel]: A panel with a image representation of the data
        """
        if len(pl_in.bench_cfg.input_vars) == 1:
            da = pl_in.bench_cfg.ds[pl_in.rv.name]
            mean = da.mean("repeat")

            # mean = mean.to_dataframe().reset_index()
            mean["repeat"] = 1
            print(mean)

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
            # print(pl_in.plt_cnt_cfg.cat_vars)
            # print(pl_in.plt_cnt_cfg.float_vars)
            # print(mean)

            # print(mean.to_dataframe().reset_index())

            fv_x = pl_in.bench_cfg.iv_repeats
            fv_y = pl_in.bench_cfg.input_vars[0]

            title = f"{pl_in.rv.name} vs ({fv_x.name} vs {fv_y.name})"
            xlabel = f"{fv_x.name} [{fv_x.units}]"
            ylabel = f"{fv_y.name} [{fv_y.units}]"
            color_label = f"{pl_in.rv.name} [{pl_in.rv.units}]"
            return [
                pn.panel(
                    px.imshow(
                        mean,
                        title=title,
                        labels={"x": xlabel, "y": ylabel, "color": color_label},
                    ),
                    name=PlotTypes.heatmap_1D,
                ),
            ]

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
