import unittest

from bencher.bench_vars import IntSweep


class TestVarSweeps(unittest.TestCase):

    def test_int_sweeps(self):
        int_sweep = IntSweep()
        self.assertEqual(int_sweep.default,0)

    