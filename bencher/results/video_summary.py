from typing import Optional
import panel as pn
import xarray as xr
from param import Parameter
from bencher.results.bench_result_base import BenchResultBase, ReduceType
from bencher.variables.results import (
    ResultImage,
)

from bencher.plotting.plot_filter import VarRange, PlotFilter
from bencher.utils import callable_name, listify
from bencher.video_writer import VideoWriter


class VideoSummaryResult(BenchResultBase):
    def to_video_summary(self, result_var: Parameter = None, **kwargs) -> Optional[pn.panel]:
        plot_filter = PlotFilter(
            float_range=VarRange(0, None),
            cat_range=VarRange(0, None),
            panel_range=VarRange(1, None),
            # repeats_range=VarRange(1,1)
        )
        matches_res = plot_filter.matches_result(
            self.plt_cnt_cfg, callable_name(self.to_video_summary_ds)
        )
        if matches_res.overall:
            ds = self.to_dataset(ReduceType.SQUEEZE)
            row = pn.Row()
            for rv in self.get_results_var_list(result_var):
                if isinstance(rv, ResultImage):
                    row.append(self.to_video_summary_ds(ds, rv, **kwargs))
            return row
        return matches_res.to_panel()

    def to_video_summary_ds(self, dataset: xr.Dataset, result_var: Parameter, **kwargs):
        vr = VideoWriter()
        da = dataset[result_var.name]
        df = da.to_dataframe()
        names = list(da.dims)
        for index, row in df.iterrows():
            index = listify(index)
            label = ", ".join(f"{a[0]}={a[1]}" for a in list(zip(names, index)))
            vr.append_png(row.values[0], label)
        vr.write_png()
        vid = pn.pane.Video(vr.filename, loop=True, **kwargs)
        vid.paused = False
        return vid
