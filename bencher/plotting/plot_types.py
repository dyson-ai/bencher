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
