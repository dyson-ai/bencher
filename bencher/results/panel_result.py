from typing import Optional
from functools import partial
import panel as pn
from param import Parameter
from bencher.results.bench_result_base import BenchResultBase, ReduceType
from bencher.results.video_result import VideoControls
from bencher.variables.results import (
    PANEL_TYPES,
)


class PanelResult(BenchResultBase):
    def to_video(self, result_var: Parameter = None, **kwargs):
        vc = VideoControls()
        return pn.Column(
            vc.video_controls(),
            self.to_panes(result_var=result_var, container=vc.video_container, **kwargs),
        )

    def to_panes(
        self, result_var: Parameter = None, target_dimension: int = 0, container=None, **kwargs
    ) -> Optional[pn.pane.panel]:
        if container is None:
            container = pn.pane.panel
        return self.map_plot_panes(
            partial(self.ds_to_container, container=container),
            hv_dataset=self.to_hv_dataset(ReduceType.SQUEEZE),
            target_dimension=target_dimension,
            result_var=result_var,
            result_types=PANEL_TYPES,
            **kwargs,
        )
