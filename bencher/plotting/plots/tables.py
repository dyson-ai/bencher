from bencher.plotting.plot_filter import PlotProvider, PlotFilter, VarRange, PlotInput
from bencher.bench_cfg import BenchCfg, PltCntCfg
from bencher.bench_vars import ParametrizedSweep

from typing import List
import panel as pn
from bencher.plotting.plot_types import AllPlotTypes


class Tables:
    """A class to display the result data in tabular form"""

    def dataframe_flat(self, pl_in: PlotInput) -> List[pn.panel]:
        """Returns a list of panel objects containing a flat dataframe."""
        df = pl_in.bench_cfg.get_dataframe()
        return [pn.pane.DataFrame(df, name=AllPlotTypes.dataframe_flat)]

    def dataframe_multi_index(self, pl_in: PlotInput) -> List[pn.panel]:
        """Returns a list of panel objects containing a multi-index dataframe."""
        df = pl_in.bench_cfg.ds.to_dataframe()
        return [pn.pane.DataFrame(df, name=AllPlotTypes.dataframe_multi_index)]

    def dataframe_mean(self, pl_in: PlotInput) -> List[pn.panel]:
        """Returns a list of panel objects containing a mean dataframe."""
        df = pl_in.bench_cfg.ds.mean("repeat").to_dataframe().reset_index()
        return [pn.pane.DataFrame(df, name=AllPlotTypes.dataframe_mean)]

    def xarray(self, pl_in: PlotInput) -> List[pn.panel]:
        """Returns a list of panel objects containing an xarray object."""
        return [pn.panel(pl_in.bench_cfg.ds, name=AllPlotTypes.xarray)]
