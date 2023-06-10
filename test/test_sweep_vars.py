import unittest
from hypothesis import given, settings, strategies as st  # pylint: disable=unused-import

from bencher.bench_vars import IntSweep


class TestVarSweeps(unittest.TestCase):
    def test_int_sweep_01(self):
        int_sweep = IntSweep(bounds=[0, 1])
        self.assertEqual(int_sweep.default, 0)
        self.assertEqual(int_sweep.values(False), [0, 1])
        self.assertEqual(int_sweep.values(True), [0, 1])

    def test_int_sweep_06(self):
        int_sweep = IntSweep(bounds=[0, 6])
        self.assertEqual(int_sweep.default, 0)
        self.assertEqual(int_sweep.values(False), [0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(int_sweep.values(True), [0, 6])

    def test_int_sweep_06_debug_sampes(self):
        int_sweep = IntSweep(bounds=[0, 6], samples_debug=4)
        self.assertEqual(int_sweep.default, 0)
        self.assertEqual(int_sweep.values(False), [0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(int_sweep.values(True), [0, 2, 4, 6])

    # todo
    # @given(st.integers(min_value=1,max_value=10))
    # def test_int_sweep(self,upper_bound):
    #     int_sweep = IntSweep(bounds=[0,upper_bound])
    #     self.assertEqual(int_sweep.default,0)
    #     self.assertEqual(len(int_sweep.values(False)),upper_bound)
    #     self.assertEqual(int_sweep.values(True),[0,upper_bound])
