from enum import auto

from strenum import StrEnum


class PlotTypes(StrEnum):
    """A enum that contains all of the inbuilt plot types.  The enum is a strEnum so the value of the enum is a str representation of the name of itself.  e.g PlotTypes.swarmplot is equal to the string 'swarmplot'.  The PlotCollection class has an add() and remove() method that takes the string name of the plot to add or remove.  You can either pass raw string, or to help reduce typos and enhance discoverability use PlotTypes.xxxxxxxx."""

    # catplot enums
    SWARMPLOT = auto()
    BARPLOT = auto()
    VIOLINPLOT = auto()
    BOXENPLOT = auto()
    BOXPLOT = auto()

    # table enums
    DATAFRAME_MULTI_INDEX = auto()
    DATAFRAME_FLAT = auto()
    DATAFRAME_MEAN = auto()
    XARRAY = auto()

    HEATMAP_2D = auto()
    HEATMAP_1D = auto()

    LINEPLOT = auto()
    LINEPLOT_HV = auto()
    LINEPLOT_HV_OVERLAY = auto()
    LINEPLOT_HV_LAYOUT = auto()
    BAR_HV = auto()
    # LINEPLOT_HV_SUBPLOT = auto()
    # LINEPLOT_HV_REPEATS = auto()

    SCATTER2D_SNS = auto()
    SCATTER_HV = auto()

    VOLUME_PLOTLY = auto()
    CONE_PLOTLY = auto()
    SURFACE_HV = auto()

    # HV_INTERACTIVE = auto()