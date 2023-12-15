from typing import Optional
import panel as pn
from bencher.plotting.plot_filter import PlotFilter, VarRange
from bencher.plotting.plot_input import PlotInput


class VolumePlot:
    def volume_plotly(self, pl_in: PlotInput) -> Optional[pn.panel]:
        if PlotFilter(
            float_range=VarRange(3, 3),
            cat_range=VarRange(-1, 0),
            vector_len=VarRange(1, 1),
            result_vars=VarRange(1, 1),
        ).matches(pl_in.plt_cnt_cfg):
            return pl_in.bench_res.to_volume()
        return None
