from __future__ import annotations
import panel as pn

from bencher.bench_cfg import PltCntCfg, BenchCfg
from bencher.bench_vars import ParametrizedSweep
from bencher.plotting.plot_filter import PlotProvider, PlotInput
import inspect


class PlotCollection:
    """A set of plot providers with filters that determine if they are able to plot the type of data in the results.  The plot collection can be customised with user defined plots or ones already defined by bencher. You can also take predefine PlotCollections defined in PlotLibrary and add or remove specific plots that you want to override.  The add and remove function accept strings, or StrEnums (which are equivalent to strings)"""

    def __init__(self) -> None:
        """A PlotCollection has a dictionary of function_name:function_pointer which are all the available types of plot. The plotters variable contains an ordered dictionary of the active plotting functions"""
        self.plotter_providers = {}
        self.plotters = {}

    def add_plotter_source(self, plotter_class_instance: PlotProvider) -> None:
        """Given a class definition that contains several plotting methods, get a list of all the methods of the class and add them to the dictionary of available plotting functions

        Args:
            plotter_class_instance (PlotProvider): A class that contains plotting methods
        """

        if not inspect.isclass(plotter_class_instance):
            self.plotter_providers |= dict(
                inspect.getmembers(plotter_class_instance, predicate=inspect.ismethod)
            )
        else:
            raise ValueError(
                "You need to pass an instance of a class not the class type, Add () to the end of the class name"
            )

    def add(self, plot_name: str) -> PlotCollection:
        """Add a plotting method to the list of active plotting functions

        Args:
            plot_name (str): The name of the plot to add.  This can either be a string, or from the StrEnum PlotTypes (which is also a string)

        Returns:
            PlotCollection: Returns a reference to this class so that you can call with a fluent api, e.g plot_coll.add(barplot).remove(swarmplot)
        """
        if plot_name in self.plotter_providers:
            self.plotters[plot_name] = self.plotter_providers[plot_name]
        else:
            raise ValueError("This plot was not found in the list of available plots")
        return self

    def remove(self, plot_name: str) -> PlotCollection:
        """Remove a plotting method from the list of active plotting functions

        Args:
            plot_name (str): The name of the plot to add.  This can either be a string, or from the StrEnum PlotTypes (which is also a string)

        Returns:
            PlotCollection: Returns a reference to this class so that you can call with a fluent api, e.g plot_coll.remove(swarmplot).add(barplot)
        """
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
