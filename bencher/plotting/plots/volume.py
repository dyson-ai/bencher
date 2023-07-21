# from typing import Optional, Tuple

# import matplotlib.pyplot as plt
# import pandas as pd
# import panel as pn
# import seaborn as sns

# from bencher.plotting.plot_filter import PlotFilter, PlotInput, VarRange
# from bencher.plotting.plot_types import PlotTypes
# from bencher.plt_cfg import PltCfgBase

# from bencher.plotting_functions import plot_volume_plotly


# class VolumePlot:
#     # shared plot filter for catplots
#     volume_filter = PlotFilter(
#         float_range=VarRange(3, 3),
#         cat_range=VarRange(0, None),
#         vector_len=VarRange(1, 1),
#         result_vars=VarRange(1, 1),
#     )

#     def volume_plotly(self, pl_in: PlotInput) -> Optional[pn.panel]:
#         if self.volume_filter.matches(pl_in.plt_cnt_cfg):

#             # return plot_volume_plotly(pl_in.bench_cfg,pl_in.rv,pl_in.)
#             # pt = pl_in.bench_cfg.to_bar()
#             pt = pl_in.bench_cfg.to_scatter()
#             # pt *= pl_in.bench_cfg.get_hv_dataset(False).to(hv.Scatter).opts(color="k", jitter=0.5)

#             return pn.Column(pt, name=PlotTypes.scatter_hv)

#         return None
