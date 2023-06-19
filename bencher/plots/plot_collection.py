import seaborn as sns
import xarray as xr
from copy import deepcopy
import panel as pn
import logging
from bencher.bench_cfg import PltCfgBase, PltCntCfg, BenchCfg, describe_benchmark
from bencher.bench_vars import ParametrizedSweep
import bencher.plotting_functions as plt_func
from bencher.plot_signature import PlotProvider
import inspect


class PlotCollection:
    def __init__(self) -> None:
        self.plotter_source = []
        self.plotter_providers = {}
        self.plotters = []

    def add_plotter_source(self, plotter: PlotProvider) -> None:
        self.plotter_source.append(plotter)
        self.plotter_providers |= dict(inspect.getmembers(plotter, predicate=inspect.ismethod))

    def add_plotter(self, plot_name: str):
        if plot_name in self.plotter_providers:
            self.plotters.append(self.plotter_providers[plot_name])

    def gather_plots(
        self, bench_cfg: BenchCfg, rv: ParametrizedSweep, plt_cnt_cfg: PltCntCfg
    ) -> pn.pane.panel:
        """This method returns a single plot based on 1 result variable and a set of input variables.  It dedeuces the correct plot type by passing it to several configuration functions that operate on the number of inputs

        Args:
            bench_cfg (BenchCfg): A config of the input vars
            rv (ParametrizedSweep): a config of the result variable
            plt_cnt_cfg (PltCntCfg): A config of how many input types there are"""

        tabs = pn.Tabs()
        for p in self.plotter_source:
            for p in p.plot(bench_cfg, rv, plt_cnt_cfg):
                tabs.append(p)
        return tabs
