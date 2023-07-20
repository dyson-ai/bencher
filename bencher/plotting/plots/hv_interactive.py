from typing import Optional
import panel as pn
import hvplot.xarray  # noqa pylint: disable=unused-import
import holoviews as hv

from bencher.plotting.plot_filter import PlotFilter, PlotInput, VarRange
from bencher.plotting.plot_types import PlotTypes  # noqa pylint: disable=unused-import


class HvInteractive:
    float_0_cat_at_least1_vec_1_res_1 = PlotFilter(
        float_range=VarRange(0, 0),
        cat_range=VarRange(1, None),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )

    # def hv_interactive(pl_in: PlotInput) -> pn.panel:
    #     ds = pl_in.bench_cfg.ds[pl_in.rv.name]
    #     return pn.panel(ds.interactive().hvplot(), label="hv interactive")

    def scatter_hv(self, pl_in: PlotInput) -> Optional[pn.panel]:
        if self.float_0_cat_at_least1_vec_1_res_1.matches(pl_in.plt_cnt_cfg):
            x = pl_in.plt_cnt_cfg.cat_vars[0]
            y = pl_in.rv
            ds = pl_in.bench_cfg.ds[pl_in.rv.name]
            title = f"{x.name} vs {y.name}"

            if pl_in.plt_cnt_cfg.cat_cnt > 1:
                c = pl_in.plt_cnt_cfg.cat_vars[1].name
                ds = ds.set_index(c)

            pt = hv.Overlay()

            pt *= ds.mean("repeat").hvplot(x=x.name, y=y.name, kind="bar")
            for r in ds.coords["repeat"]:
                pt *= ds.sel(repeat=r).hvplot(
                    x=x.name,
                    y=y.name,
                    kind="scatter",
                    rot=45,
                    color="black",
                )

            return pn.Column(pt.opts(height=600, title=title), name="scatter_hv")

        return None

    def lineplot_hv(self, pl_in: PlotInput) -> Optional[pn.panel]:
        if PlotFilter(
            float_range=VarRange(1, None),
            cat_range=VarRange(-1, -1),
            vector_len=VarRange(1, 1),
            result_vars=VarRange(1, 1),
        ).matches(pl_in.plt_cnt_cfg):
            print("lineplothv")
            print(pl_in.plt_cnt_cfg.cat_cnt, pl_in.plt_cnt_cfg.cat_vars)
            return pn.panel(pl_in.bench_cfg.to_curve(), name=PlotTypes.lineplot_hv)
        return None
