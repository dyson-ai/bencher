import bencher as bch

# All the examples will be using the data structures and benchmark function defined in this file
# from bencher.example.benchmark_data import ExampleBenchCfgIn, ExampleBenchCfgOut, bench_function

import random


class CrashCfg(bch.ParametrizedSweep):
    crash_threshold = bch.FloatSweep(default=0.5, samples=6, bounds=[0.2, 0.5])


class CrashResult(bch.ParametrizedOutput):
    value = bch.ResultVar()


def crashy_fn(crash_cfg: CrashCfg) -> CrashResult:
    res = CrashResult()
    res.value = random.uniform(0.0, 1.0)

    if res.value < crash_cfg.crash_threshold:
        raise RuntimeError("I crashed for no good reason ;P")

    return res


def example_sample_cache(run_cfg: bch.BenchRunCfg) -> bch.Bench:
    """This example shows how to use the use_sample_cache option to deal with unreliable functions and to continue benchmarking using previously calcualted results even if the code crashing during the run

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """

    bencher = bch.Bench("example_sample_cache", crashy_fn, CrashCfg)

    # here we sample the input variable theta and plot the value of output1. The (noisy) function is sampled 20 times so you can see the distribution
    bencher.plot_sweep(
        title="Example Crashy Function with the sample_cache",
        input_vars=[CrashCfg.param.crash_threshold],
        result_vars=[CrashResult.param.value],
        description=example_sample_cache.__doc__,
        run_cfg=run_cfg,
    )
    return bencher


if __name__ == "__main__":
    ex_run_cfg = bch.BenchRunCfg()
    ex_run_cfg.repeats = 2
    ex_run_cfg.use_sample_cache = True
    # ex_run_cfg.clear_sample_cache = True

    example_sample_cache(ex_run_cfg).plot()
