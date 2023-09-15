import unittest
from hypothesis import given, strategies as st  # pylint: disable=unused-import
import pytest
from bencher.variables.inputs import IntSweep, EnumSweep, StringSweep, BoolSweep, FloatSweep
from enum import auto
from strenum import StrEnum


class TestVarSweeps(unittest.TestCase):
    def test_int_sweep_01(self):
        int_sweep = IntSweep(bounds=[0, 1])
        self.assertEqual(int_sweep.default, 0)
        self.assertListEqual(int_sweep.values(0), [0, 1])

    def test_int_sweep_06(self):
        int_sweep = IntSweep(bounds=[0, 6])
        self.assertEqual(int_sweep.default, 0)
        self.assertListEqual(int_sweep.values(0), [0, 1, 2, 3, 4, 5, 6])

    def test_int_sweep_06_debug_sampes(self):
        int_sweep = IntSweep(bounds=[0, 6])
        self.assertEqual(int_sweep.default, 0)
        self.assertListEqual(int_sweep.values(0), [0, 1, 2, 3, 4, 5, 6])

    def test_int_sweep_10_debug_sampes(self):
        int_sweep = IntSweep(bounds=[0, 10])
        self.assertEqual(int_sweep.default, 0)
        self.assertListEqual(int_sweep.values(0), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_int_sweep_10_with_values_(self):
        int_sweep = IntSweep(bounds=[0, 10])
        self.assertEqual(int_sweep.default, 0)
        self.assertListEqual(int_sweep.values(0), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertListEqual(int_sweep.values(2), [0, 10])
        self.assertListEqual(int_sweep.values(3), [0, 5, 10])

    def test_int_sweep_level_10_with_values_(self):
        int_sweep = IntSweep(bounds=[0, 10])
        self.assertListEqual(int_sweep.values(1), [0])
        self.assertListEqual(int_sweep.values(2), [0, 10])
        self.assertListEqual(int_sweep.values(3), [0, 5, 10])
        self.assertListEqual(int_sweep.values(4), [0, 2, 5, 7, 10])
        self.assertListEqual(int_sweep.values(5), [0, 1, 2, 3, 5, 6, 7, 8, 10])
        self.assertListEqual(int_sweep.values(6), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_int_sweep_level_10_with_values_and_step(self):
        int_sweep = IntSweep(bounds=[0, 10], step=2, samples=4)
        self.assertListEqual(int_sweep.values(1), [0])
        self.assertListEqual(int_sweep.values(2), [0, 10])
        self.assertListEqual(int_sweep.values(3), [0, 5, 10])
        self.assertListEqual(int_sweep.values(4), [0, 2, 5, 7, 10])
        self.assertListEqual(int_sweep.values(5), [0, 1, 2, 3, 5, 6, 7, 8, 10])
        self.assertListEqual(int_sweep.values(6), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_int_sweep_level_1000_with_values_(self):
        int_sweep = IntSweep(default=100, bounds=[100, 1000])
        self.assertListEqual(int_sweep.values(1), [100])
        self.assertListEqual(int_sweep.values(2), [100, 1000])
        self.assertListEqual(int_sweep.values(3), [100, 550, 1000])
        self.assertListEqual(int_sweep.values(4), [100, 325, 550, 775, 1000])
        self.assertListEqual(int_sweep.values(5), [100, 212, 325, 437, 550, 662, 775, 887, 1000])
        self.assertListEqual(
            int_sweep.values(6),
            [100, 156, 212, 268, 325, 381, 437, 493, 550, 606, 662, 718, 775, 831, 887, 943, 1000],
        )

    def test_float_sweep(self):
        float_sweep = FloatSweep(bounds=[0, 1])

        self.assertListEqual(list(float_sweep.values(1)), [0.0])
        self.assertListEqual(list(float_sweep.values(2)), [0.0, 1.0])
        self.assertListEqual(list(float_sweep.values(3)), [0.0, 0.5, 1.0])
        self.assertListEqual(list(float_sweep.values(4)), [0.0, 0.25, 0.5, 0.75, 1.0])

    def test_float_sweep_with_step(self):
        float_sweep = FloatSweep(bounds=[0, 1], step=0.01)

        self.assertListEqual(list(float_sweep.values(1)), [0.0])
        self.assertListEqual(list(float_sweep.values(2)), [0.0, 0.99])
        self.assertListEqual(list(float_sweep.values(3)), [0.0, 0.49, 0.99])
        self.assertListEqual(list(float_sweep.values(4)), [0.0, 0.24, 0.49, 0.74, 0.99])

    def test_float_step(self):
        float_sweep = FloatSweep(bounds=[0, 1], step=0.1)

        self.assertListEqual(
            list(float_sweep.values(0)),
            [
                0.0,
                0.1,
                0.2,
                0.30000000000000004,
                0.4,
                0.5,
                0.6000000000000001,
                0.7000000000000001,
                0.8,
                0.9,
            ],
        )

        float_sweep2 = FloatSweep(bounds=[0, 0.9], step=0.1)
        # note that it does not return the upper bound of 0.9 even though it a multiple of 0.1
        self.assertListEqual(
            list(float_sweep2.values(0)),
            [
                0.0,
                0.1,
                0.2,
                0.30000000000000004,
                0.4,
                0.5,
                0.6000000000000001,
                0.7000000000000001,
                0.8,
            ],
        )

    def test_enum_sweep_level(self):
        class Enum1(StrEnum):
            VAL1 = auto()
            VAL2 = auto()
            VAL3 = auto()
            VAL4 = auto()

        enum_sweep = EnumSweep(Enum1)

        self.assertListEqual(enum_sweep.values(1), [Enum1.VAL1])

        self.assertListEqual(enum_sweep.values(2), [Enum1.VAL1, Enum1.VAL4])

        self.assertListEqual(enum_sweep.values(3), [Enum1.VAL1, Enum1.VAL2, Enum1.VAL4])
        self.assertListEqual(enum_sweep.values(4), [Enum1.VAL1, Enum1.VAL2, Enum1.VAL3, Enum1.VAL4])
        self.assertListEqual(enum_sweep.values(5), [Enum1.VAL1, Enum1.VAL2, Enum1.VAL3, Enum1.VAL4])

    def test_bool_default(self) -> None:
        bool_sweep_true = BoolSweep(default=True)
        self.assertTrue(bool_sweep_true.default)

        bool_sweep_false = BoolSweep(default=False)
        self.assertFalse(bool_sweep_false.default)

    def test_bool_sweep_level(self):
        bool_sweep = BoolSweep()

        self.assertListEqual(bool_sweep.values(1), [True])
        self.assertListEqual(bool_sweep.values(2), [True, False])
        self.assertListEqual(bool_sweep.values(3), [True, False])

    def test_string_sweep_level(self):
        string_sweep = StringSweep(["VAL1", "VAL2", "VAL3", "VAL4"])
        self.assertListEqual(string_sweep.values(1), ["VAL1"])
        self.assertListEqual(string_sweep.values(2), ["VAL1", "VAL4"])
        self.assertListEqual(string_sweep.values(3), ["VAL1", "VAL2", "VAL4"])
        self.assertListEqual(string_sweep.values(4), ["VAL1", "VAL2", "VAL3", "VAL4"])
        self.assertListEqual(string_sweep.values(5), ["VAL1", "VAL2", "VAL3", "VAL4"])

    # @given(st.integers(min_value=1, max_value=20))
    # def test_int_sweep_samples(self, samples):
    #     int_sweep = IntSweep(bounds=[0, 10], samples=samples)
    #     self.assertEqual(int_sweep.default, 0)
    #     self.assertEqual(len(int_sweep.values(0)), samples)

    @pytest.mark.skip
    @given(st.integers(min_value=1, max_value=10))
    def test_int_sweep_samples_all(self, samples):
        int_sweep = IntSweep(bounds=[0, 10], samples=samples)
        self.assertEqual(int_sweep.default, 0)
        self.assertEqual(len(int_sweep.values(0)), samples)
