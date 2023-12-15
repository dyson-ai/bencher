from typing import Optional

import panel as pn
import plotly.graph_objs as go
import logging
import xarray as xr

from bencher.bench_cfg import BenchCfg
from bencher.variables.parametrised_sweep import ParametrizedSweep

from bencher.plotting.plot_filter import PlotFilter, VarRange
from bencher.plotting.plot_input import PlotInput

from bencher.plotting.plot_types import PlotTypes

from bencher.plotting.plt_cnt_cfg import PltCfgBase, PltCntCfg


class VolumePlot:
    def volume_plotly(self, pl_in: PlotInput, **opts) -> Optional[pn.panel]:
        if PlotFilter(
            float_range=VarRange(3, 3),
            cat_range=VarRange(-1, 0),
            vector_len=VarRange(1, 1),
            result_vars=VarRange(1, 1),
        ).matches(pl_in.plt_cnt_cfg):
            return pl_in.bench_res.to_volume(pl_in.rv)
            sns_cfg = PltCfgBase()
            sns_cfg.y = pl_in.rv.name
            xr_cfg = plot_float_cnt_3(sns_cfg, pl_in.plt_cnt_cfg, pl_in.bench_res.bench_cfg.debug)
            xr_cfg.param.update(**opts)
            return plot_volume_plotly(pl_in.bench_res, pl_in.rv, xr_cfg)
        return None
