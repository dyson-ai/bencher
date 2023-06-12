from bencher.plot_signature import (
    PlotProvider,
    PlotSignature,
    VarRange,
    PltCntCfg,
    PltCfgBase,
)
from bencher import BenchCfg, ResultVec, ResultVar, BenchPlotter
from typing import List
import seaborn as sns
import panel as pn

class Catplot(PlotProvider):

    @staticmethod
    def filter(plot_sig: PlotSignature):
        if plot_sig.float_cnt ==0:
            if plot_sig.cat_cnt>0:
                if plot_sig.vector_len==0:
                    return True
        return False



    @staticmethod
    def plot_float_cnt_0(plot_sig: PlotSignature, bench_cfg: BenchCfg) -> pn.pane:
        """A function for determining the plot settings if there are 0 float variable and updates the PltCfgBase

        Args:
            sns_cfg (PltCfgBase): See PltCfgBase definition
            plt_cnt_cfg (PltCntCfg): See PltCntCfg definition

        Returns:
            PltCfgBase: See PltCfgBase definition
        """

        if Catplot().filter(plot_sig):

            df = Catplot.plot_setup(plot_sig, bench_cfg)
            sns_cfg.plot_callback = sns.catplot
            sns_cfg.kind = "swarm"

            # as more cat variables are added, map them to these plot axes
            cat_axis_order = ["x", "row", "col", "hue"]
            sns_cfg = BenchPlotter.axis_mapping(cat_axis_order, sns_cfg, plt_cnt_cfg)

        return sns_cfg

    @staticmethod
    def plot_setup(plot_sig: PlotSignature, bench_cfg: BenchCfg):
        plt.figure(figsize=(4, 4))        
        df = bench_cfg.ds[rv.name].to_dataframe().reset_index()
        return df

    @staticmethod
    def plot_postprocess():
        
        try:
            fg = sns_cfg.plot_callback(data=df, **sns_cfg.as_sns_args())
            if bench_cfg.over_time:
            for ax in fg.axes.flatten():
                for tick in ax.get_xticklabels():
                    tick.set_rotation(45)

        fg.set_xlabels(label=sns_cfg.xlabel, clear_inner=True)
        fg.set_ylabels(label=sns_cfg.ylabel, clear_inner=True)
        fg.fig.suptitle(sns_cfg.title)
        plt.tight_layout()

        if bench_cfg.save_fig:
            save_fig(bench_cfg, sns_cfg)
        return pn.panel(plt.gcf())
        except Exception as e:
            return pn.pane.Markdown(
                f"Was not able to plot becuase of exception:{e} \n this is likely due to too many NAN values"
            )

            # TODO try to set this during the initial plot rather than after
       
