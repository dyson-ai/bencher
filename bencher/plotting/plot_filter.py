from __future__ import annotations

from dataclasses import dataclass

from bencher.bench_cfg import BenchCfg, PltCntCfg
from bencher.bench_vars import ParametrizedSweep


class VarRange:
    def __init__(self, lower_bound: int = 0, upper_bound: int = -1) -> None:
        """A VarRange represents the bounded and unbounded ranges of integers.  This class is used to define filters for various variable types.  For example by defining cat_var = VarRange(0,0), calling matches(0) will return true, but any other integer will not match.  You can also have unbounded ranges for example VarRange(2,None) will match to 2,3,4... up to infinity. for By default the lower and upper bounds are set to -1 so so that no matter what value is passsed to matches() will return false.  Matches only takes 0 and positive integers.

        Args:
            lower_bound (int, optional): The smallest acceptable value to matches(). Passing None will result in a lower bound of 0 (as matches only accepts positive integers). Defaults to 0.
            upper_bound (int, optional): The largest acceptable value to matches().  Passing None will result in no upper bound. Defaults to -1.
        """
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def matches(self, val: int) -> bool:
        """Checks that a value is within the variable range.  lower_bound and upper_bound are inclusive (lower_bound<=val<=upper_bound )

        Args:
            val (int): A positive integer representing a number of items

        Returns:
            bool: True if the items is within the range, False otherwise.

        Raises:
            ValueError: If val < 0
        """
        if val < 0:
            raise ValueError("val must be >= 0")
        if self.lower_bound is not None:
            lower_match = val >= self.lower_bound
        else:
            lower_match = True

        if self.upper_bound is not None:
            upper_match = val <= self.upper_bound
        else:
            upper_match = True

        return lower_match and upper_match

    def __repr__(self) -> str:
        return f"VarRange(lower_bound={self.lower_bound}, upper_bound={self.upper_bound})"


class PlotFilter:
    def __init__(
        self,
        float_range: VarRange = VarRange(),
        cat_range: VarRange = VarRange(),
        vector_len: VarRange = VarRange(1, 1),
        result_vars: VarRange = VarRange(1, 1),
    ) -> None:
        """A class for representing the types of results a plot is able to represent.

        Args:
            float_range (VarRange, optional): The range of float varibles the plot supports. Defaults to VarRange().
            cat_range (VarRange, optional): The range of categorical varibles the plot supports. Defaults to VarRange().
            vector_len (VarRange, optional): The range of vector lengths the plot supports. Defaults to VarRange(1, 1).
            result_vars (VarRange, optional): The range of number of result varibles the plot supports. Defaults to VarRange(1, 1).
        """

        self.float_range = float_range
        self.cat_range = cat_range
        self.vector_len = vector_len
        self.result_vars = result_vars

    def matches(self, plt_cng_cfg: PltCntCfg) -> bool:
        """Checks if the result data signature matches the type of data the plot is able to display.

        Args:
            plt_cng_cfg (PltCntCfg): The plot count configuration to check.

        Returns:
            bool: True if the configuration matches the filter, False otherwise.
        """

        return (
            self.float_range.matches(plt_cng_cfg.float_cnt)
            and self.cat_range.matches(plt_cng_cfg.cat_cnt)
            and self.vector_len.matches(plt_cng_cfg.vector_len)
            and self.result_vars.matches(plt_cng_cfg.result_vars)
        )


@dataclass
class PlotInput:
    """A dataclass that contains all the information needed to plot
    Args:
        bench_cfg (BenchCfg): The benchmark configuration used to generate the result data
        rv (ParametrizedSweep): The result variable to plot
        plt_cnt_cfg (PltCntCfg): The number and types of variable to plot
    """

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
