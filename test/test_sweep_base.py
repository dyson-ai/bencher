import unittest

from bencher.example.benchmark_data import AllSweepVars
import bencher as bch


class TestSweepBase(unittest.TestCase):
    def test_with_samples(self) -> None:
        """Check that using with_samples does not have side effects"""

        sweep_samples_before = AllSweepVars.param.var_float.values()
        custom_samples = AllSweepVars.param.var_float.with_samples(5).values()
        sweep_samples_after = AllSweepVars.param.var_float.values()

        self.assertEqual(str(sweep_samples_before), str(sweep_samples_after))
        self.assertNotEqual(str(sweep_samples_before), str(custom_samples))

    def test_with_const(self) -> None:
        """Check that setting a const returns the right const"""

        res = AllSweepVars.param.var_float.with_const(5)

        self.assertEqual(res[1], 5)

    def test_setting_const(self) -> None:
        """Check that setting a const returns the right const"""

        explorer = AllSweepVars()
        bench = bch.Bench("tst_cnst", explorer.call)

        # AllSweepVars.param.var_float.with_const(5)

        consts = explorer.get_input_defaults()
        consts_len = len(consts)

        res = bench.plot_sweep(
            "tst",
            input_vars=[AllSweepVars.param.var_float],
            const_vars=consts,
        )

        consts_after = [i[0] for i in res.const_vars]

        # print(consts_after)

        self.assertEqual(consts_len, len(consts))
        self.assertEqual(consts_len - 1, len(consts_after))

        self.assertTrue(AllSweepVars.param.var_float not in consts)
        self.assertTrue(explorer.param.var_float not in consts)

        # self.assertTrue(False)

        # self.assertEqual(res[1], 5)
