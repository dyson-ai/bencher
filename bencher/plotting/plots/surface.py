from typing import Optional
import panel as pn
import logging
import xarray as xr
import holoviews as hv

from bencher.plotting.plot_filter import PlotFilter, VarRange
from bencher.plotting.plot_input import PlotInput

from bencher.plotting.plt_cnt_cfg import PltCfgBase, PltCntCfg
from bencher.plotting.plot_types import PlotTypes
from bencher.variables.results import ResultVar


# class SurfacePlot:
