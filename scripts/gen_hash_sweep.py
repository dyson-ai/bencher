#!/bin/python

"""Use a separate python process to test hashes are the same across processes"""

from bencher.example.benchmark_data import AllSweepVars


if __name__ == "__main__":
    ex = AllSweepVars()
    print(ex.__repr__())
    print(hash(ex))
