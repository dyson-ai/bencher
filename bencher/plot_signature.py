from __future__ import annotations
import param
from bencher.bench_cfg import PltCntCfg, BenchCfg
from bencher.bench_vars import ParametrizedSweep
from typing import Callable


class VarRange:
    def __init__(self, lower_bound=-1, upper_bound=-1) -> None:
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


class PlotFilter:
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

    def matches(self, plt_cng_cfg: PltCntCfg) -> bool:
        return (
            self.float_range.matches(plt_cng_cfg.float_cnt)
            and self.cat_range.matches(plt_cng_cfg.cat_cnt)
            and self.vector_len.matches(plt_cng_cfg.vector_len)
            and self.result_vars.matches(plt_cng_cfg.result_vars)
        )


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
