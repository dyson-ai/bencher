import logging
from copy import deepcopy
from typing import List
import panel as pn

from bencher.results.panel_result import PanelResult
from bencher.results.result_plotly import ResultPlotly
from bencher.results.holoview_result import HoloviewResult
# from bencher.plt_cfg import BenchPlotter

class BenchResult(PanelResult, ResultPlotly, HoloviewResult):
    """Contains the results of the benchmark and has methods to cast the results to various datatypes and graphical representations"""

    def __init__(self, bench_cfg) -> None:
        PanelResult.__init__(self, bench_cfg)
        ResultPlotly.__init__(self, bench_cfg)
        HoloviewResult.__init__(self, bench_cfg)

    # def plot(self) -> List[pn.panel]:
    #     """Given the dataset result of a benchmark run, automatically dedeuce how to plot the data based on the types of variables that were sampled

    #     Args:
    #         bench_cfg (BenchCfg): Information on how the benchmark was sampled and the resulting data

    #     Returns:
    #         pn.pane: A panel containing plot results
    #     """
    #     plot_cols = pn.Column()
    #     plot_cols.append(self.bench_cfg.summarise_sweep(name="Plots View"))

    #     if self.bench_cfg.over_time:
    #         if len(self.ds.coords["over_time"]) > 1:
    #             plot_cols.append(pn.pane.Markdown("## Results Over Time"))
    #             plot_cols.append(BenchPlotter.plot_results_row(self))
    #         else:
    #             plot_cols.append(
    #                 pn.pane.Markdown("Results over time needs at least 2 time snapshots to plot")
    #             )

    #         plot_cols.append(pn.pane.Markdown("## Most Recent Results"))
    #         bench_deep = deepcopy(self)  # TODO do this in the future without copying
    #         bench_deep.over_time = False
    #         bench_deep.iv_time = []
    #         last_time = bench_deep.ds.coords["over_time"][-1]
    #         try:
    #             bench_deep.ds = bench_deep.ds.sel(over_time=last_time)
    #             plot_cols.append(BenchPlotter.plot_results_row(bench_deep))
    #         except ValueError as e:
    #             warning = f"failed to load historical data: {e}"
    #             plot_cols.append(pn.pane.Markdown(warning))
    #             logging.warning(warning)

    #     else:
    #         plot_cols.append(pn.pane.Markdown("## Results"))
    #         plot_cols.append(BenchPlotter.plot_results_row(self))

    #     plot_cols.append(pn.pane.Markdown(f"{self.bench_cfg.post_description}"))
    #     return plot_cols
