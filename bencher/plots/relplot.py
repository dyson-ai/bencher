from bencher.plotting_functions import PlotProvider
from bencher import BenchPlotter
from bencher.bench_cfg import PltCntCfg, PltCfgBase
# from typing import List
import seaborn as sns


class RelPlot(PlotProvider):
    def plot_float_cnt_1(
        self, sns_cfg: PltCfgBase, plt_cnt_cfg: PltCntCfg
    ) -> PltCfgBase:
        """A function for determining the plot settings if there is 1 float variable and updates the PltCfgBase

        Args:
            sns_cfg (PltCfgBase): See PltCfgBase definition
            plt_cnt_cfg (PltCntCfg): See PltCntCfg definition

        Returns:
            PltCfgBase: See PltCfgBase definition
        """

        if plt_cnt_cfg.float_cnt == 1:
            sns_cfg.x = plt_cnt_cfg.float_vars[0].name
            sns_cfg.kind = "line"
            sns_cfg.plot_callback = sns.relplot

            # as more cat variables are added, map them to these plot axes
            cat_axis_order = ["hue", "row", "col", "hue"]

            sns_cfg = BenchPlotter.axis_mapping(cat_axis_order, sns_cfg, plt_cnt_cfg)

        return sns_cfg
