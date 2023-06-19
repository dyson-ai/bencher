from __future__ import annotations
import param
from bencher.bench_cfg import PltCntCfg

# from bencher.plotting_functions import Plot


class VarRange:
    # lower_bound = param.Integer(0)
    # upper_bound = param.Integer(0)

    def __init__(self, lower_bound=-1, upper_bound=-1) -> None:
        # assert upper_bound >= lower_bound
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def matches_range(self, var_range: VarRange) -> bool:
        return (
            var_range.lower_bound >= self.lower_bound and var_range.upper_bound <= self.upper_bound
        )

    def matches(self, val: int):
        if self.lower_bound is not None:
            lower_match = val >= self.lower_bound
        else:
            lower_match = True

        if self.upper_bound is not None:
            upper_match = val <= self.upper_bound
        else:
            upper_match = True

        return lower_match and upper_match

        # return self.lower_bound <= val and val <= self.upper_bound


class PlotFilter:
    # def __init__(self) -> None:
    #     self.float_range = VarRange(0, 0)
    #     self.cat_range = VarRange(0, 0)
    #     self.vector_len = VarRange(1, 1)
    #     self.result_vars = VarRange(1, 1)

    def __init__(
        self,
        float_range: VarRange = VarRange(),
        cat_range: VarRange = VarRange(),
        vector_len: VarRange = VarRange(1, 1),
        result_vars: VarRange = VarRange(1, 1),
    ) -> None:
        self.float_range = float_range
        self.cat_range = cat_range
        self.vector_len = vector_len
        self.result_vars = result_vars

    # def matches_sig(self, plot_sig: PlotSignature):
    #     return (
    #         self.float_range.matches(plot_sig.float_range)
    #         and self.cat_range.matches(plot_sig.cat_range)
    #         and self.vector_len.matches(plot_sig.vector_len)
    #         and self.result_vars.matches(plot_sig.result_vars)
    #     )

    def matches(self, plt_cng_cfg: PltCntCfg) -> bool:
        return (
            self.float_range.matches(plt_cng_cfg.float_cnt)
            and self.cat_range.matches(plt_cng_cfg.cat_cnt)
            and self.vector_len.matches(plt_cng_cfg.vector_len)
            and self.result_vars.matches(plt_cng_cfg.result_vars)
        )


from abc import ABC, abstractmethod


class PlotProvider:
    def plot(self, bench_cfg: BenchCfg, rv: ParametrizedSweep, plt_cnt_cfg: PltCntCfg):
        all_plots = []
        for p in self.plots:
            all_plots.extend(p(bench_cfg, rv, plt_cnt_cfg))
        return all_plots

    def register_plot(self, plot_fn: Callable):
        if not hasattr(self, "plots"):
            self.plots = []
        self.plots.append(plot_fn)
