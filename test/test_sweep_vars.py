import unittest
from hypothesis import given, strategies as st  # pylint: disable=unused-import
import pytest
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

    @given(st.integers(min_value=1, max_value=10))
    def test_int_sweep_samples(self, samples):
        int_sweep = IntSweep(bounds=[0, 10], samples=samples)
        self.assertEqual(int_sweep.default, 0)
        self.assertEqual(len(int_sweep.values(False)), samples)

    @given(st.integers(min_value=1, max_value=10))
    def test_int_sweep_debug_samples(self, samples_debug):
        int_sweep = IntSweep(bounds=[0, 10], samples_debug=samples_debug)
        self.assertEqual(int_sweep.default, 0)
        self.assertEqual(len(int_sweep.values(True)), samples_debug)

    @pytest.mark.skip
    @given(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=10))
    def test_int_sweep_samples_all(self, samples, samples_debug):
        int_sweep = IntSweep(bounds=[0, 10], samples=samples)
        self.assertEqual(int_sweep.default, 0)
        self.assertEqual(len(int_sweep.values(False)), samples)
        self.assertEqual(len(int_sweep.values(True)), samples_debug)
