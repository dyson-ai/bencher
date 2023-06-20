from bencher.plots.plot_collection import PlotCollection
from bencher.plots.catplot import Catplot
from bencher.plots.tables import Tables

from strenum import StrEnum
from enum import auto


class AllPlotTypes(StrEnum):
    """A enum that contains all of the inbuilt plot types.  The enum is a strEnum so the value of the enum is a str representation of the name of itself.  e.g AllPlotTypes.swarmplot is equal to the string 'swarmplot'.  The PlotCollection class has an add() and remove() method that takes the string name of the plot to add or remove.  You can either pass raw string, or to help reduce typos and enhance discoverability use AllPlottypes.xxxxxxxx."""

    # catplot enums
    swarmplot = auto()
    barplot = auto()
    violinplot = auto()
    boxenplot = auto()

    # table enums
    dataframe_multi_index = auto()
    dataframe_flat = auto()
    dataframe_mean = auto()
    xarray = auto()


class PlotLibrary:
    """This class is a collection of static factory methods that define sets of plots.  It provides a sensible default PlotCollection out of the box but also enables the creation of custom PlotCollections"""

    @staticmethod
    def setup_sources() -> PlotCollection:
        """Shared method that collects all the possible plot types.  This is used by all the other methods that select different subsections of the plots

        Returns:
            PlotCollection: A PlotCollection with sources of plots defined, but none selected
        """
        plt_col = PlotCollection()
        plt_col.add_plotter_source(Catplot())
        plt_col.add_plotter_source(Tables())
        return plt_col

    @staticmethod
    def default() -> PlotCollection:
        """Default PlotCollection.  This set of plots should provide a reasonable set of plots that cover the most common data plotting use cases

        Returns:
            PlotCollection: sensible default for PlotCollection
        """
        plt_col = PlotLibrary.setup_sources()
        plt_col.add(AllPlotTypes.swarmplot)
        return plt_col

    @staticmethod
    def tables() -> PlotCollection:
        """Display only table summaries of the data

        Returns:
            PlotCollection: Only table plots
        """
        plt_col = PlotLibrary.setup_sources()
        plt_col.add(AllPlotTypes.dataframe_multi_index)
        plt_col.add(AllPlotTypes.dataframe_mean)
        return plt_col

    @staticmethod
    def all() -> PlotCollection:
        """Display the data in every possible way. All plots are included

        Returns:
            PlotCollection: All possible plots
        """
        plt_col = PlotLibrary.setup_sources()
        for pt in [p for p in AllPlotTypes]:  # iterate through all plot enums
            plt_col.add(pt)
        return plt_col
