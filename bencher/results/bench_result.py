from __future__ import annotations
from typing import List
import panel as pn

from bencher.results.panel_result import PanelResult
from bencher.results.plotly_result import PlotlyResult
from bencher.results.holoview_result import HoloviewResult
from bencher.results.bench_result_base import EmptyContainer

# from bencher.results.heatmap_result import HeatMapResult

# from bencher.results.seaborn_result import SeabornResult


class BenchResult(PlotlyResult, HoloviewResult):

    """Contains the results of the benchmark and has methods to cast the results to various datatypes and graphical representations"""

    def __init__(self, bench_cfg) -> None:
        PlotlyResult.__init__(self, bench_cfg)
        HoloviewResult.__init__(self, bench_cfg)

    @staticmethod
    def default_plot_callbacks():
        return [
            HoloviewResult.to_bar,
            HoloviewResult.to_scatter_jitter,
            HoloviewResult.to_curve,
            HoloviewResult.to_line,
            HoloviewResult.to_heatmap,
            # self.to_surface_hv,
            PlotlyResult.to_volume,
            PanelResult.to_video,
            PanelResult.to_panes,
        ]

    @staticmethod
    def plotly_callbacks():
        return [HoloviewResult.to_surface_hv, PlotlyResult.to_volume]

    def to_auto(
        self,
        plot_list: List[callable] = None,
        **kwargs,
    ) -> List[pn.panel]:
        self.plt_cnt_cfg.print_debug = False

        if plot_list is None:
            plot_list = BenchResult.default_plot_callbacks()

        row = EmptyContainer(pn.Row())
        for plot_callback in plot_list:
            # if self.plt_cnt_cfg.print_debug:
            print(f"checking: {plot_callback.__name__}")
            # the callbacks are passed from the static class definition, so self needs to be passed before the plotting callback can be called

            # row.append(partial(plot_callback, self, **kwargs))

            row.append(plot_callback(self, **kwargs))

            # row.append(self.map_plots(partial(plot_callback, self, **kwargs)))

        self.plt_cnt_cfg.print_debug = False
        if len(row.pane) == 0:
            row.append(
                pn.pane.Markdown("No Plotters are able to represent these results", **kwargs)
            )
        return row.pane

    def to_auto_da(self):
        pass

    def to_auto_plots(self, **kwargs) -> List[pn.panel]:
        """Given the dataset result of a benchmark run, automatically dedeuce how to plot the data based on the types of variables that were sampled

        Args:
            bench_cfg (BenchCfg): Information on how the benchmark was sampled and the resulting data

        Returns:
            pn.pane: A panel containing plot results
        """
        plot_cols = pn.Column()
        plot_cols.append(self.bench_cfg.to_sweep_summary(name="Plots View"))
        plot_cols.append(self.to_auto(**kwargs))
        plot_cols.append(self.bench_cfg.to_post_description())
        return plot_cols

        # if self.bench_cfg.over_time:
        #     if len(self.ds.coords["over_time"]) > 1:
        #         plot_cols.append(pn.pane.Markdown("## Results Over Time"))
        #         plot_cols.append(self.plot_results_row())
        #     else:
        #         plot_cols.append(
        #             pn.pane.Markdown("Results over time needs at least 2 time snapshots to plot")
        #         )

        #     plot_cols.append(pn.pane.Markdown("## Most Recent Results"))
        #     bench_deep = deepcopy(self)  # TODO do this in the future without copying
        #     bench_deep.bench_cfg.over_time = False
        #     bench_deep.bench_cfg.iv_time = []
        #     last_time = bench_deep.ds.coords["over_time"][-1]
        #     try:
        #         bench_deep.ds = bench_deep.ds.sel(over_time=last_time)
        #         plot_cols.append(bench_deep.plot_results_row())
        #     except ValueError as e:
        #         warning = f"failed to load historical data: {e}"
        #         plot_cols.append(pn.pane.Markdown(warning))
        #         logging.warning(warning)

        # else:
        #     plot_cols.append(pn.pane.Markdown("## Results"))
        #     plot_cols.append(self.plot_results_row())

        # plot_cols.append(pn.pane.Markdown(f"{self.bench_cfg.post_description}"))

        # plot_cols.append(self.to_auto())
        # return plot_cols

    # def plot_results_row(self) -> pn.Row:
    #     """Given a BenchCfg, plot each result variable and add to a panel row

    #     Returns:
    #         pn.Row: A panel row with plots in it
    #     """
    #     # todo remove the scroll and make it resize dynamically
    #     plot_rows = pn.Row(name=self.bench_cfg.bench_name)

    #     plt_cnt_cfg = PltCntCfg.generate_plt_cnt_cfg(self.bench_cfg)

    #     for rv in self.bench_cfg.result_vars:
    #         plt_cnt_cfg.result_vars = 1
    #         if type(rv) == ResultVec:
    #             plt_cnt_cfg.vector_len = rv.size
    #         else:
    #             plt_cnt_cfg.vector_len = 1

    #         if self.bench_cfg.plot_lib is not None:
    #             print(plt_cnt_cfg)
    #             plot_rows.append(self.bench_cfg.plot_lib.gather_plots(self, rv, plt_cnt_cfg))
    #         # todo enable this check in future pr
    #         # if len(plot_rows) == 0:  # use the old plotting method as a backup
    #         plot_rows.append(pn.panel(self.plot_result_variable(rv, plt_cnt_cfg)))

    #     return plot_rows

    # def plot_result_variable(self, rv: ParametrizedSweep, plt_cnt_cfg: PltCntCfg) -> pn.Column:
    #     """This method returns a single plot based on 1 result variable and a set of input variables.  It dedeuces the correct plot type by passing it to several configuration functions that operate on the number of inputs

    #     Args:
    #         rv (ParametrizedSweep): a config of the result variable
    #         plt_cnt_cfg (PltCntCfg): A config of how many input types there are

    #     Raises:
    #         FileExistsError: If there are file naming conflicts

    #     Returns:
    #         PlotResult: A summary of all the data used to generate a plot
    #     """
    #     surf_col = pn.Column()

    #     sns_cfg = PltCfgBase()
    #     sns_cfg.y = rv.name  # by default the result variable is always plotted on the y axis

    #     if plt_cnt_cfg.float_cnt < 2:
    #         # set a marker for time series to its easy to see the measurment points
    #         if self.bench_cfg.over_time:
    #             sns_cfg.marker = "."
    #         if plt_cnt_cfg.float_cnt == 0:
    #             sns_cfg = BenchPlotter.plot_float_cnt_0(sns_cfg, plt_cnt_cfg)
    #         elif plt_cnt_cfg.float_cnt == 1:
    #             sns_cfg = BenchPlotter.plot_float_cnt_1(sns_cfg, plt_cnt_cfg)
    #         sns_cfg = BenchPlotter.get_axes_and_title(rv, sns_cfg, plt_cnt_cfg)
    #         surf_col.append(self.plot_sns(rv, sns_cfg))

    #     return surf_col


# class BenchPlotter:
#     """A deprecated class for handling benchmark plotting logic. Deprecation is still a work in progress"""

#     @staticmethod
#     def axis_mapping(cat_axis_order, sns_cfg: PltCfgBase, plt_cnt_cfg: PltCntCfg) -> PltCfgBase:
#         """A function for determining the plot settings if there are 0 float variable and updates the PltCfgBase

#         Args:
#             sns_cfg (PltCfgBase): See PltCfgBase definition
#             plt_cnt_cfg (PltCntCfg): See PltCntCfg definition

#         Returns:
#             PltCfgBase: See PltCfgBase definition
#         """
#         sns_dict = {}
#         for i, v in enumerate(plt_cnt_cfg.cat_vars):
#             axis = cat_axis_order[i]
#             sns_dict[axis] = v.name

#         sns_cfg.param.update(**sns_dict)

#         return sns_cfg

#     @staticmethod
#     def get_axes_and_title(
#         rv: ParametrizedSweep, sns_cfg: PltCfgBase, plt_cnt_cfg: PltCntCfg
#     ) -> PltCntCfg:
#         """Work out the axes label and plot tite

#         Args:
#             rv (ParametrizedSweep): result variable
#             sns_cfg (PltCfgBase): plotting config
#             plt_cnt_cfg (PltCntCfg): plot count config

#         Returns:
#             PltCfgBase: plot count config with titles added
#         """
#         all_vars = plt_cnt_cfg.float_vars + plt_cnt_cfg.cat_vars
#         xvar = None
#         for i in all_vars:
#             if i.name == sns_cfg.x:
#                 xvar = i.units
#         if xvar is not None:
#             sns_cfg.xlabel = f"{sns_cfg.x} [{xvar}]"
#         sns_cfg.ylabel = f"{sns_cfg.y} [{rv.units}]"
#         sns_cfg.title = f"{sns_cfg.x} vs {sns_cfg.y}"
#         return sns_cfg

#     @staticmethod
#     def plot_float_cnt_0(sns_cfg: PltCfgBase, plt_cnt_cfg: PltCntCfg) -> PltCfgBase:
#         """A function for determining the plot settings if there are 0 float variable and updates the PltCfgBase

#         Args:
#             sns_cfg (PltCfgBase): See PltCfgBase definition
#             plt_cnt_cfg (PltCntCfg): See PltCntCfg definition

#         Returns:
#             PltCfgBase: See PltCfgBase definition
#         """

#         if plt_cnt_cfg.float_cnt == 0:
#             sns_cfg.plot_callback = sns.catplot
#             sns_cfg.kind = "swarm"

#             # as more cat variables are added, map them to these plot axes
#             cat_axis_order = ["x", "row", "col", "hue"]
#             sns_cfg = BenchPlotter.axis_mapping(cat_axis_order, sns_cfg, plt_cnt_cfg)

#         return sns_cfg

#     @staticmethod
#     def plot_float_cnt_1(sns_cfg: PltCfgBase, plt_cnt_cfg: PltCntCfg) -> PltCfgBase:
#         """A function for determining the plot settings if there is 1 float variable and updates the PltCfgBase

#         Args:
#             sns_cfg (PltCfgBase): See PltCfgBase definition
#             plt_cnt_cfg (PltCntCfg): See PltCntCfg definition

#         Returns:
#             PltCfgBase: See PltCfgBase definition
#         """

#         if plt_cnt_cfg.float_cnt == 1:
#             sns_cfg.x = plt_cnt_cfg.float_vars[0].name
#             sns_cfg.kind = "line"
#             sns_cfg.plot_callback = sns.relplot

#             # as more cat variables are added, map them to these plot axes
#             cat_axis_order = ["hue", "row", "col", "hue"]

#             sns_cfg = BenchPlotter.axis_mapping(cat_axis_order, sns_cfg, plt_cnt_cfg)

#         return sns_cfg

#     @staticmethod
#     def plot_float_cnt_2(plt_cnt_cfg: PltCntCfg, rv: ResultVar, debug: bool) -> PltCfgBase:
#         """A function for determining the plot settings if there are 2 float variable and updates the PltCfgBase
#         Args:
#             sns_cfg (PltCfgBase): See PltCfgBase definition
#             plt_cnt_cfg (PltCntCfg): See PltCntCfg definition
#         Returns:
#             PltCfgBase: See PltCfgBase definition
#         """
#         xr_cfg = PltCfgBase()
#         if plt_cnt_cfg.float_cnt == 2:
#             logging.info(f"surface plot: {rv.name}")
#             xr_cfg.plot_callback_xra = xr.plot.plot
#             xr_cfg.x = plt_cnt_cfg.float_vars[0].name
#             xr_cfg.y = plt_cnt_cfg.float_vars[1].name
#             xr_cfg.xlabel = f"{xr_cfg.x} [{plt_cnt_cfg.float_vars[0].units}]"
#             xr_cfg.ylabel = f"{xr_cfg.y} [{plt_cnt_cfg.float_vars[1].units}]"
#             xr_cfg.zlabel = f"{rv.name} [{rv.units}]"
#             xr_cfg.title = f"{rv.name} vs ({xr_cfg.x} and {xr_cfg.y})"

#             if plt_cnt_cfg.cat_cnt >= 1:
#                 logging.info("surface plot with 1 categorical")
#                 xr_cfg.row = plt_cnt_cfg.cat_vars[0].name
#                 xr_cfg.num_rows = len(plt_cnt_cfg.cat_vars[0].values(debug))
#             if plt_cnt_cfg.cat_cnt >= 2:
#                 logging.info("surface plot with 2> categorical")
#                 xr_cfg.col = plt_cnt_cfg.cat_vars[1].name
#                 xr_cfg.num_cols = len(plt_cnt_cfg.cat_vars[1].values(debug))
#         return xr_cfg
