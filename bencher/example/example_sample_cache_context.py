import bencher as bch


from strenum import StrEnum
from enum import auto


class ExampleEnum(StrEnum):
    value_1 = auto()
    value_2 = auto()
    # value3 = auto()
    # value4 = auto()


class Cfg(bch.ParametrizedSweep):
    enum1 = bch.EnumSweep(ExampleEnum)
    result = bch.ResultVar()


def bench_function(cfg: Cfg):
    return {"result": float(str(cfg.enum1)[-1])}


def example_cache_context() -> bch.Bench:
    run_cfg = bch.BenchRunCfg()
    run_cfg.use_sample_cache = True
    run_cfg.clear_sample_cache = True  # clear the first time
    run_cfg.sample_cache_include_bench_context = False

    bencher = bch.Bench("bench_context", bench_function, Cfg)

    bencher.plot_sweep(title="Benchmark enum=value_1", const_vars=[(
        Cfg.param.enum1, ExampleEnum.value_1)], result_vars=[Cfg.param.result], run_cfg=run_cfg)

    assert bencher.worker_wrapper_call_count == 1
    assert bencher.worker_fn_call_count == 1
    assert bencher.worker_cache_call_count == 0

    bencher.clear_call_counts()
    bencher.plot_sweep(title="Benchmark enum=value_2", const_vars=[
                       (Cfg.param.enum1, ExampleEnum.value_2)], result_vars=[Cfg.param.result], run_cfg=run_cfg)

    assert bencher.worker_wrapper_call_count == 1
    assert bencher.worker_fn_call_count == 1
    assert bencher.worker_cache_call_count == 0

    run_cfg.clear_sample_cache = False  # clear the first time

    bencher.clear_call_counts()
    res = bencher.plot_sweep(title="Benchmark enum=[value_1,value_2] combined", input_vars=[
                             Cfg.param.enum1], result_vars=[Cfg.param.result], run_cfg=run_cfg)

    assert bencher.worker_wrapper_call_count == 2
    assert bencher.worker_fn_call_count == 0
    assert bencher.worker_cache_call_count == 2

    return bencher


if __name__ == "__main__":
    example_cache_context().plot()
