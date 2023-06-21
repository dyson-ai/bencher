import seaborn as sns
import xarray as xr
from copy import deepcopy
import panel as pn
import logging
from bencher.bench_cfg import PltCfgBase, PltCntCfg, BenchCfg, describe_benchmark
from bencher.bench_vars import ParametrizedSweep
import bencher.plotting_functions as plt_func
from bencher.plotting.plot_filter import PlotProvider, PlotInput
import inspect
from collections import OrderedDict


class PlotCollection:
    def __init__(self) -> None:
        self.plotter_source = []
        self.plotter_providers = {}
        self.plotters = OrderedDict()

    def add_plotter_source(self, plotter: PlotProvider) -> None:
        self.plotter_source.append(plotter)
        self.plotter_providers |= dict(inspect.getmembers(plotter, predicate=inspect.ismethod))

    def add(self, plot_name: str):
        if plot_name in self.plotter_providers:
            self.plotters[plot_name] = self.plotter_providers[plot_name]
        return self

    def remove(self, plot_name: str):
        self.plotters.pop(plot_name)
        return self

    def gather_plots(
        self, bench_cfg: BenchCfg, rv: ParametrizedSweep, plt_cnt_cfg: PltCntCfg
    ) -> pn.pane.panel:
        """This method returns a single plot based on 1 result variable and a set of input variables.  It dedeuces the correct plot type by passing it to several configuration functions that operate on the number of inputs

        Args:
            bench_cfg (BenchCfg): A config of the input vars
            rv (ParametrizedSweep): a config of the result variable
            plt_cnt_cfg (PltCntCfg): A config of how many input types there are"""

        tabs = pn.Tabs()
        for p in self.plotters.values():
            plots = p(PlotInput(bench_cfg, rv, plt_cnt_cfg))
            for p in plots:
                tabs.append(p)
        return tabs
