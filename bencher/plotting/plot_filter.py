from __future__ import annotations
from bencher.bench_cfg import PltCntCfg, BenchCfg
from bencher.bench_vars import ParametrizedSweep


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


from dataclasses import dataclass


@dataclass
class PlotInput:
    bench_cfg: BenchCfg
    rv: ParametrizedSweep
    plt_cnt_cfg: PltCntCfg


class PlotProvider:
    """A base class for code that displays or plots data. Each class that inherits provides plotting methods and a filter that specifies what the plot is capable of displaying"""

    # commonly used filters that are shared across classes
    float_1_cat_any_vec_1_res_1_ = PlotFilter(
        float_range=VarRange(0, 0),
        cat_range=VarRange(0, None),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )
