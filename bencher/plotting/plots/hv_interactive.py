from typing import Optional, Tuple

import panel as pn

from bencher.plotting.plot_filter import PlotFilter, PlotInput, VarRange
from bencher.plotting.plot_types import PlotTypes
from bencher.plt_cfg import PltCfgBase

import hvplot.xarray  # noqa
import holoviews as hv


class HvInteractive():

    float_0_cat_at_least1_vec_1_res_1 = PlotFilter(
        float_range=VarRange(0, 0),
        cat_range=VarRange(1, None),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )

    def hv_interactive(pl_in: PlotInput) -> pn.panel:
        ds = pl_in.bench_cfg.ds[pl_in.rv.name]
        return pn.panel(ds.interactive().hvplot(), label="hv interactive")

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
                    x=x.name, y=y.name, kind="scatter", rot=45, color="black"
                )

            return pn.Column(pt.opts(height=600, title=title), name=PlotTypes.scatter_hv)

        return None

    # @staticmethod
    # def plot_postprocess(fg: plt.figure, sns_cfg: PltCfgBase, name: str) -> Optional[pn.panel]:
    #     fg.fig.suptitle(sns_cfg.title)
    #     fg.set_xlabels(label=sns_cfg.xlabel, clear_inner=True)
    #     fg.set_ylabels(label=sns_cfg.ylabel, clear_inner=True)
    #     plt.tight_layout()
    #     return pn.panel(fg.fig, name=name)

    # def catplot_common(self, pl_in: PlotInput, kind: str, name: str) -> Optional[pn.panel]:
    #     if self.float_0_cat_at_least1_vec_1_res_1.matches(pl_in.plt_cnt_cfg):
    #         df, sns_cfg = self.plot_setup(pl_in)
    #         sns_cfg.kind = kind
    #         fg = sns.catplot(df, **sns_cfg.as_sns_args())
    #         return self.plot_postprocess(fg, sns_cfg, name)
    #     return None

    # def swarmplot(self, pl_in: PlotInput) -> Optional[pn.panel]:
    #     return self.catplot_common(pl_in, "swarm", PlotTypes.swarmplot)

    # def violinplot(self, pl_in: PlotInput) -> Optional[pn.panel]:
    #     return self.catplot_common(pl_in, "violin", PlotTypes.violinplot)

    # def boxplot(self, pl_in: PlotInput) -> Optional[pn.panel]:
    #     return self.catplot_common(pl_in, "box", PlotTypes.boxplot)

    # def barplot(self, pl_in: PlotInput) -> Optional[pn.panel]:
    #     return self.catplot_common(pl_in, "bar", PlotTypes.barplot)

    # def boxenplot(self, pl_in: PlotInput) -> Optional[pn.panel]:
    #     return self.catplot_common(pl_in, "boxen", PlotTypes.boxenplot)
