from bencher.plotting_functions import (
    PlotProvider,
    PlotSignature,
    VarRange,
    PltCntCfg,
    PltCfgBase,
)
from bencher import BenchCfg, ResultVec, ResultVar, BenchPlotter
from typing import List
import seaborn as sns


class catplot(PlotProvider):
    def plot_float_cnt_0(self,sns_cfg: PltCfgBase, plt_cnt_cfg: PltCntCfg) -> PltCfgBase:
        """A function for determining the plot settings if there are 0 float variable and updates the PltCfgBase

        Args:
            sns_cfg (PltCfgBase): See PltCfgBase definition
            plt_cnt_cfg (PltCntCfg): See PltCntCfg definition

        Returns:
            PltCfgBase: See PltCfgBase definition
        """

        if plt_cnt_cfg.float_cnt == 0:
            sns_cfg.plot_callback = sns.catplot
            sns_cfg.kind = "swarm"

            # as more cat variables are added, map them to these plot axes
            cat_axis_order = ["x", "row", "col", "hue"]
            sns_cfg = BenchPlotter.axis_mapping(cat_axis_order, sns_cfg, plt_cnt_cfg)

        return sns_cfg
