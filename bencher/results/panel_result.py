from typing import Optional
from functools import partial
import panel as pn
from param import Parameter
import holoviews as hv
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
        self,
        result_var: Parameter = None,
        hv_dataset=None,
        target_dimension: int = 0,
        container=None,
        level: int = None,
        **kwargs,
    ) -> Optional[pn.pane.panel]:
        if hv_dataset is None:
            hv_dataset = self.to_hv_dataset(ReduceType.SQUEEZE, level=level)
        elif not isinstance(hv_dataset, hv.Dataset):
            hv_dataset = hv.Dataset(hv_dataset)
        return self.map_plot_panes(
            partial(self.ds_to_container, container=container),
            hv_dataset=hv_dataset,
            target_dimension=target_dimension,
            result_var=result_var,
            result_types=PANEL_TYPES,
            **kwargs,
        )


def zip_results1D(args):
    first_el = [a[0] for a in args]
    out = pn.Column()
    for a in zip(*first_el):
        row = pn.Row()
        row.append(a[0])
        for a1 in range(1, len(a[1])):
            row.append(a[a1][1])
        out.append(row)
    return out


def zip_results1D1(args):
    first_el = args
    container_args = {"styles": {}}
    container_args["styles"]["border-bottom"] = f"{2}px solid grey"
    out = pn.Column()
    for a in zip(*first_el):
        row = pn.Row(**container_args)
        row.append(a[0][0])
        for a1 in range(0, len(a)):
            row.append(a[a1][1])
        out.append(row)
    return out
