
import seaborn as sns
import xarray as xr
from copy import deepcopy
import panel as pn
import logging
from bencher.bench_cfg import PltCfgBase, PltCntCfg, BenchCfg, describe_benchmark
from bencher.bench_vars import ParametrizedSweep
import bencher.plotting_functions as plt_func
from plot_signature import PlotProvider


class PlotLibrary:

    def __init__(self) -> None:
        self.plotters = []

    def add_plotter(self,plotter:PlotProvider) -> None:
        self.plotters.append(plotter)

    def gather_plots(self, bench_cfg: BenchCfg, rv: ParametrizedSweep, plt_cnt_cfg: PltCntCfg)->pn.pane.Pane:
        """This method returns a single plot based on 1 result variable and a set of input variables.  It dedeuces the correct plot type by passing it to several configuration functions that operate on the number of inputs

        Args:
            bench_cfg (BenchCfg): A config of the input vars
            rv (ParametrizedSweep): a config of the result variable
            plt_cnt_cfg (PltCntCfg): A config of how many input types there are"""

        coln =  pn.Column()    
        for p in self.plotters:
            plot = p.
            coln.append


            