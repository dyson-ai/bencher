from enum import auto

from strenum import StrEnum


class PlotTypes(StrEnum):
    """A enum that contains all of the inbuilt plot types.  The enum is a strEnum so the value of the enum is a str representation of the name of itself.  e.g PlotTypes.swarmplot is equal to the string 'swarmplot'.  The PlotCollection class has an add() and remove() method that takes the string name of the plot to add or remove.  You can either pass raw string, or to help reduce typos and enhance discoverability use PlotTypes.xxxxxxxx."""

    # catplot enums
    swarmplot = auto()
    barplot = auto()
    violinplot = auto()
    boxenplot = auto()
    boxplot = auto()

    # table enums
    dataframe_multi_index = auto()
    dataframe_flat = auto()
    dataframe_mean = auto()
    xarray = auto()

    heatmap_2D = auto()
    heatmap_1D = auto()

    lineplot = auto()
    lineplot_hv = auto()
    lineplot_hv_overlay = auto()
    lineplot_hv_layout = auto()
    bar_hv = auto()
    # lineplot_hv_subplot = auto()
    # lineplot_hv_repeats = auto()

    scatter2D_sns = auto()
    scatter_hv = auto()

    volume_plotly = auto()
    cone_plotly = auto()
    surface_hv = auto()

    # hv_interactive = auto()
