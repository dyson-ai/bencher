from bencher.plots.plot_collection import PlotCollection
from bencher.plots.catplot import Catplot
from bencher.plots.tables import Tables

from strenum import StrEnum
from enum import auto


class AllPlotTypes(StrEnum):
    # table enums
    dataframe_raw = auto()
    dataframe_mean = auto()
    xarray = auto()

    # catplot enums
    swarmplot = auto()
    barplot = auto()
    violinplot = auto()
    boxenplot = auto()


class PlotLibrary:
    @staticmethod
    def setup_sources():
        plt_col = PlotCollection()
        plt_col.add_plotter_source(Catplot())
        plt_col.add_plotter_source(Tables())
        return plt_col

    @staticmethod
    def default() -> PlotCollection:
        plt_col = PlotLibrary.setup_sources()
        plt_col.add(AllPlotTypes.swarmplot)
        return plt_col
