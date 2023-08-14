import unittest

from bencher.example.benchmark_data import AllSweepVars


class TestSweepBase(unittest.TestCase):
    def test_with_samples(self) -> None:
        """Check that using with_samples does not have side effects"""
        AllSweepVars()

        sweep_samples_before = AllSweepVars.param.var_float.values()
        custom_samples = AllSweepVars.param.var_float.with_samples(5).values()
        sweep_samples_after = AllSweepVars.param.var_float.values()

        self.assertEqual(str(sweep_samples_before), str(sweep_samples_after))
        self.assertNotEqual(str(sweep_samples_before), str(custom_samples))

    def test_with_const(self) -> None:
        """Check that setting a const returns the right const"""

        res = AllSweepVars.param.var_float.with_const(5)

        self.assertEqual(res[1], 5)
