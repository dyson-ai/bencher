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
            input_vars=[AllSweepVars.param.var_float.with_samples(3)],
            const_vars=consts,
        )

        consts_after = [i[0] for i in res.const_vars]

        self.assertEqual(consts_len, len(consts))
        self.assertEqual(consts_len - 1, len(consts_after))

        self.assertTrue(AllSweepVars.param.var_float not in consts)
        self.assertTrue(explorer.param.var_float not in consts)

    def test_override_const(self) -> None:
        """Check that setting a const returns the right const"""

        explorer = AllSweepVars()
        bch.Bench("tst_cnst", explorer.call)

        consts = explorer.get_input_defaults()
        const_override = explorer.get_input_defaults([AllSweepVars.param.var_float.with_const(2)])

        # const_override_class = AllSweepVars.get_input_defaults(
        #     [AllSweepVars.param.var_float.with_const(2)]
        # )

        # const_override_instance = explorer.get_input_defaults(
        #     [explorer.param.var_float.with_const(2)]
        # )

        print(consts)
        print("overridden")
        print(const_override)

        self.assertEqual(consts[0][1], 5)
        self.assertEqual(const_override[0][1], 2)
        # self.assertEqual(const_override_class[0][1], 2)
        # self.assertEqual(const_override_instance[0][1], 2)

        self.assertNotEqual(consts, const_override)
        self.assertEqual(len(consts), len(const_override))

    def test_override_defaults(self):
        exp = AllSweepVars()

        class_defaults = AllSweepVars.get_input_defaults(
            [AllSweepVars.param.var_float.with_const(3)]
        )
        self.assertEqual(class_defaults[0][1], 3)

        # check that the defaults have not been modified
        default_defaults = AllSweepVars.get_input_defaults()
        self.assertEqual(default_defaults[0][1], 5)

        instance_defaults = exp.get_input_defaults([exp.param.var_float.with_const(2)])
        self.assertEqual(instance_defaults[0][1], 2)

    def test_with_sample_values(self):
        vals = AllSweepVars.param.var_float.with_sample_values([0, 1]).values(False)
        self.assertEqual(vals[0], 0)
        self.assertEqual(vals[1], 1)

        defaults = AllSweepVars.param.var_float.values(False)
        self.assertEqual(defaults[9], 10)


if __name__ == "__main__":
    TestSweepBase().test_override_defaults()
