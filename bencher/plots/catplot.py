from bencher.plot_signature import (
    PlotProvider,
    PlotFilter,
    VarRange,
    PltCntCfg,
    PltCfgBase,
)
from bencher import BenchCfg, ResultVec, ResultVar, BenchPlotter
from typing import List
import seaborn as sns
import panel as pn


class Catplot(PlotProvider):
    def swarmplot(self, plot_sig: PltCntCfg, bench_cfg: BenchCfg) -> pn.pane:
        """A function for determining the plot settings if there are 0 float variable and updates the PltCfgBase
        Args:
            sns_cfg (PltCfgBase): See PltCfgBase definition
            plt_cnt_cfg (PltCntCfg): See PltCntCfg definition
        Returns:
            PltCfgBase: See PltCfgBase definition
        """

        if PlotFilter(
            float_range=VarRange(0, 0),
            cat_range=VarRange(0, None),
            vector_len=VarRange(1, 1),
        ).matches(plot_sig):
            df = self.plot_setup(plot_sig, bench_cfg)
            sns_cfg.kind = "swarm"

            # as more cat variables are added, map them to these plot axes
            cat_axis_order = ["x", "row", "col", "hue"]
            sns_cfg = BenchPlotter.axis_mapping(cat_axis_order, sns_cfg, plt_cnt_cfg)

        return sns_cfg

    def plot_setup(self, plot_sig: PlotFilter, bench_cfg: BenchCfg):
        plt.figure(figsize=(4, 4))
        df = bench_cfg.ds[rv.name].to_dataframe().reset_index()
        return df
