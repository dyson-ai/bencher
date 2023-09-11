import bencher as bch

from bencher.example.example_categorical import example_categorical
from bencher.example.example_floats import example_floats

from bencher.example.example_floats2D import example_floats2D
from bencher.example.example_pareto import example_pareto
from bencher.example.example_simple_cat import example_1D_cat
from bencher.example.example_simple_float import example_1D_float

from bencher.example.example_float_cat import run_example_float_cat
from bencher.example.example_time_event import run_example_time_event
from bencher.example.example_float3D import example_floats3D
from bencher.example.example_custom_sweep import example_custom_sweep

# from bencher.example.example_workflow import example_floats2D_workflow, example_floats3D_workflow
from bencher.example.example_holosweep import example_holosweep
from bencher.example.example_holosweep_tap import example_holosweep_tap
from bencher.example.optuna.example_optuna import optuna_rastrigin
from bencher.example.example_sample_cache import example_sample_cache


if __name__ == "__main__":
    run_cfg = bch.BenchRunCfg()
    bench_runner = bch.BenchRunner(run_cfg=run_cfg)

    bench_runner.add_run(example_categorical)
    bench_runner.add_run(example_floats)
    bench_runner.add_run(example_floats2D)
    bench_runner.add_run(example_floats3D)
    bench_runner.add_run(example_1D_cat)
    bench_runner.add_run(example_1D_float)
    bench_runner.add_run(example_pareto)
    bench_runner.add_run(run_example_float_cat)
    bench_runner.add_run(run_example_time_event)
    bench_runner.add_run(example_custom_sweep)
    bench_runner.add_run(example_holosweep)
    bench_runner.add_run(example_holosweep_tap)




    bench_runner.run(level=2, show=True)
