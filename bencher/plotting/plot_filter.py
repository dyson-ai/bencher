from __future__ import annotations
import logging
from dataclasses import dataclass
from bencher.plotting.plt_cnt_cfg import PltCntCfg


class VarRange:
    """A VarRange represents the bounded and unbounded ranges of integers.  This class is used to define filters for various variable types.  For example by defining cat_var = VarRange(0,0), calling matches(0) will return true, but any other integer will not match.  You can also have unbounded ranges for example VarRange(2,None) will match to 2,3,4... up to infinity. for By default the lower and upper bounds are set to -1 so so that no matter what value is passsed to matches() will return false.  Matches only takes 0 and positive integers."""

    def __init__(self, lower_bound: int = 0, upper_bound: int = -1) -> None:
        """
        Args:
            lower_bound (int, optional): The smallest acceptable value to matches(). Passing None will result in a lower bound of 0 (as matches only accepts positive integers). Defaults to 0.
            upper_bound (int, optional): The largest acceptable value to matches().  Passing None will result in no upper bound. Defaults to -1 which results in a range with no matches.
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

    def matches_info(self, val, print_msg, msg: str):
        match = self.matches(val)
        if print_msg:
            logging.info(f"{msg}\t{match}\t{self.lower_bound}>= {val} <={self.upper_bound}")
        return match

    def __str__(self) -> str:
        return f"VarRange(lower_bound={self.lower_bound}, upper_bound={self.upper_bound})"


@dataclass
class PlotFilter:
    """A class for representing the types of results a plot is able to represent."""

    float_range: VarRange = VarRange()
    cat_range: VarRange = VarRange()
    vector_len: VarRange = VarRange(1, 1)
    result_vars: VarRange = VarRange(1, 1)
    panel_range: VarRange = VarRange(0, 0)
    repeats_range: VarRange = VarRange(1, None)

    def matches(self, plt_cng_cfg: PltCntCfg) -> bool:
        """Checks if the result data signature matches the type of data the plot is able to display.

        Args:
            plt_cng_cfg (PltCntCfg): The plot count configuration to check.

        Returns:
            bool: True if the configuration matches the filter, False otherwise.
        """

        deb = plt_cng_cfg.print_debug
        float_match = self.float_range.matches_info(plt_cng_cfg.float_cnt, deb, "float")
        cat_match = self.cat_range.matches_info(plt_cng_cfg.cat_cnt, deb, "cat")
        vector_match = self.vector_len.matches_info(plt_cng_cfg.vector_len, deb, "vec")
        result_var_match = self.result_vars.matches_info(plt_cng_cfg.result_vars, deb, "result")
        panel_match = self.panel_range.matches_info(plt_cng_cfg.panel_cnt, deb, "panel")
        repeats_match = self.panel_range.matches_info(plt_cng_cfg.repeats, deb, "repeat")

        overall = (
            float_match
            and cat_match
            and vector_match
            and result_var_match
            and panel_match
            and repeats_match
        )

        if plt_cng_cfg.print_debug:
            logging.info(f"overall:\t{overall}")

        return overall

    # def info(self,plt_cng_cfg.float_cnt):
    # logging.info(f"float {self.float_range}={plt_cng_cfg.float_cnt} {float_match}")

    # def __repr__(self) -> str:
    # return f"{self.float_range}"
    #   print(f"float {plt_cnt_cfg.float_cnt}")
    #         print(f"cat {plt_cnt_cfg.cat_cnt}")
    #         print(f"vec {plt_cnt_cfg.vector_len}")


class PlotProvider:
    """A base class for code that displays or plots data. Each class that inherits provides plotting methods and a filter that specifies what the plot is capable of displaying"""

    # commonly used filters that are shared across classes
    float_1_cat_any_vec_1_res_1_ = PlotFilter(
        float_range=VarRange(0, 0),
        cat_range=VarRange(0, None),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )
