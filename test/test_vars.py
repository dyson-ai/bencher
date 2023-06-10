import unittest
import pytest
import os

from bencher.example.benchmark_data import AllSweepVars


def get_sweep_hash_isolated_process():
    """get has values from a separate process as by default hashes across process are not the same"""
    os.system(
        "python3 -c 'from bencher.example.benchmark_data import AllSweepVars;ex = AllSweepVars();print(ex.__repr__());print(hash(ex))' > hashed_vars_comparison_tmp"
    )
    res = open("hashed_vars_comparison_tmp", "r", encoding="utf-8").read()
    os.remove("hashed_vars_comparison_tmp")
    return res


class TestBencherHashing(unittest.TestCase):
    def test_sweep_hashes(self):
        """check that separate instances with identical data have the same hash"""
        ex = AllSweepVars()
        ex2 = AllSweepVars()

        self.assertEqual(hash(ex.var_float), hash(ex2.var_float))
        self.assertEqual(hash(ex.var_int), hash(ex2.var_int))
        self.assertEqual(hash(ex.var_enum), hash(ex2.var_enum))

        print(ex.__repr__())
        print(ex2.__repr__())

        self.assertEqual(hash(ex), hash(ex2))

    def test_hash_sweep(self) -> None:
        """hash values only seem to not match if run in a separate process, so run the hash test in separate processes"""

        asv = AllSweepVars()
        asv2 = AllSweepVars()

        self.assertEqual(
            hash(asv), hash(asv2), "The classes should have equal hash when it has identical values"
        )

        asv2.var_float = 1
        self.assertNotEqual(
            hash(asv),
            hash(asv2),
            "The classes should not have equal hash when they have different values",
        )

    def test_hash_sweep_isolated(self) -> None:
        """hash values only seem to not match if run in a separate process, so run the hash test in separate processes"""

        self.assertNotEqual(
            len(get_sweep_hash_isolated_process()), 0, "make sure the hash is getting returned"
        )

        self.assertEqual(
            get_sweep_hash_isolated_process(),
            get_sweep_hash_isolated_process(),
            "make sure the hashes are equal",
        )


print(get_sweep_hash_isolated_process())
