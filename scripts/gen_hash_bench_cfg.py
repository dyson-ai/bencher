#!/bin/python
"""Use a separate python process to test hashes are the same across processes"""

from bencher.bencher import BenchCfg
from bencher.example.benchmark_data import ExampleBenchCfgIn, ExampleBenchCfgOut


if __name__ == "__main__":
    cfg1 = BenchCfg(
        input_vars=[ExampleBenchCfgIn.param.theta, ExampleBenchCfgIn.param.noise_distribution],
        result_vars=[ExampleBenchCfgOut.param.out_sin],
        const_vars=[ExampleBenchCfgIn.param.noisy],
        repeats=5,
        over_time=False,
    )
    print(hash(cfg1))
