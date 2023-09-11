import bencher as bch


# from bencher.example.example_workflow import example_floats2D_workflow, example_floats3D_workflow
from bencher.example.example_sample_cache import example_sample_cache


if __name__ == "__main__":
    run_cfg = bch.BenchRunCfg()
    bench_runner = bch.BenchRunner(run_cfg=run_cfg)

    # bench_runner.add_run(example_categorical)
    # bench_runner.add_run(example_floats)
    # bench_runner.add_run(example_floats2D)
    # bench_runner.add_run(example_floats3D)
    # bench_runner.add_run(example_1D_cat)
    # bench_runner.add_run(example_1D_float)
    # bench_runner.add_run(example_pareto)
    # bench_runner.add_run(run_example_float_cat)
    # bench_runner.add_run(run_example_time_event)
    # bench_runner.add_run(example_custom_sweep)
    # bench_runner.add_run(example_holosweep)
    # bench_runner.add_run(example_holosweep_tap)
    # bench_runner.add_run(optuna_rastrigin)
    bench_runner.add_run(example_sample_cache)

    bench_runner.run(level=2, show=True)
