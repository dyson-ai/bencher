from typing import List, Tuple
import seaborn as sns
import panel as pn
import matplotlib.pyplot as plt
import pandas as pd
from bencher.plotting.plot_filter import PlotFilter, VarRange, PlotInput
from bencher.plt_cfg import PltCfgBase
from bencher.plotting.plot_types import PlotTypes

import plotly.graph_objects as go
import plotly.express as px


class Plots2D:
    # shared plot filter for 2d plots
    plot_filter = PlotFilter(
        float_range=VarRange(2, 2),
        cat_range=VarRange(0, 0),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )

    def imshow(self, pl_in: PlotInput) -> List[pn.panel]:
        """use the imshow plotting method to display 2D data

        Args:
            pl_in (PlotInput): The data to plot

        Returns:
            List[pn.panel]: A panel with a image representation of the data
        """
        if self.plot_filter.matches(pl_in.plt_cnt_cfg):
            da = pl_in.bench_cfg.ds[pl_in.rv.name]
            mean = da.mean("repeat")
            return [pn.panel(px.imshow(mean), name=PlotTypes.imshow)]
        return []
