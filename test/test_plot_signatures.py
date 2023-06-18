import unittest
from bencher.plot_signature import VarRange, PlotFilter
from hypothesis import given, settings, strategies as st

from bencher.bench_cfg import PltCntCfg


class TestVarRange(unittest.TestCase):
    # @given(st.integers(), st.integers())
    # def test_matches_none(self, min_val, max_val):
    #     self.assertFalse(VarRange().matches(VarRange(min_val, max_val)))

    def test_matches_zero(self):
        zero_case = VarRange(0, 0)
        # self.assertFalse(zero_case.matches(-1))
        self.assertTrue(zero_case.matches(0))
        self.assertFalse(zero_case.matches(1))

    def test_matches_upto(self):
        var_range = VarRange(0, 1)
        # self.assertFalse(zero_case.matches(-1))
        self.assertTrue(var_range.matches(0))
        self.assertTrue(var_range.matches(1))
        self.assertFalse(var_range.matches(2))

    def test_matches_none(self):
        var_range = VarRange(0, None)
        # self.assertFalse(zero_case.matches(-1))
        self.assertTrue(var_range.matches(0))
        self.assertTrue(var_range.matches(1))
        self.assertTrue(var_range.matches(100))
