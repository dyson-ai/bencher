from __future__ import annotations
import param


class VarRange:
    # lower_bound = param.Integer(0)
    # upper_bound = param.Integer(0)

    def __init__(self, lower_bound=0, upper_bound=0) -> None:
        assert upper_bound >= lower_bound
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def matches(self, var_range: VarRange) -> bool:
        return (
            var_range.lower_bound >= self.lower_bound and var_range.upper_bound <= self.upper_bound
        )


class PlotSignature:
    def __init__(self) -> None:
        self.float_range = VarRange(0, 0)
        self.cat_range = VarRange(0, 0)
        self.vector_len = VarRange(1, 1)
        self.result_vars = VarRange(1, 1)

    def matches(self, plot_sig: PlotSignature):
        return (
            self.float_range.matches(plot_sig.float_range)
            and self.cat_range.matches(plot_sig.cat_range)
            and self.vector_len.matches(plot_sig.vector_len)
            and self.result_vars.matches(plot_sig.result_vars)
        )


class PlotProvider:
    def __init__(self) -> None:
        pass
