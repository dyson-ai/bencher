import unittest
import pytest
import subprocess
import os

from bencher.example.benchmark_data import AllSweepVars


def get_sweep_hash_isolated_process():
    """get has values from a separate process as by default hashes across process are not the same"""
    workspace = os.getenv("DYSON_WORKSPACE")
    result = subprocess.run(
        [f"{workspace}/src/common/bencher/scripts/gen_hash_sweep.py"],
        stdout=subprocess.PIPE,
        check=False,
    )
    return result.stdout

#TODO enable this again
@pytest.mark.skip
class TestBencherHashing(unittest.TestCase):
    def test_python_hash_seed(self) -> None:
        self.assertTrue(os.getenv("PYTHONHASHSEED"), "42")

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
        self.assertEqual(get_sweep_hash_isolated_process(), get_sweep_hash_isolated_process())
