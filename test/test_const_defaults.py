import unittest
from copy import deepcopy
import bencher as bch
from bencher.example.meta.example_meta import BenchableObject


class TestBenchMeta(unittest.TestCase):
    def test_repeats_equal(self):

        bench = bch.Bench("bench", BenchableObject())

        consts = BenchableObject().get_input_defaults_override(float1=1)

        const_deep = deepcopy(consts)

        bench.const_vars = consts

        res1 = bench.plot_sweep("repeats", input_vars=["float1"], const_vars=consts)
        res1 = bench.plot_sweep("repeats", input_vars=["float2"], const_vars=consts)

        self.assertEqual(const_deep, consts)


if __name__ == "__main__":
    unittest.main()
