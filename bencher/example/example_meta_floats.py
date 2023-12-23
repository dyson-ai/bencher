import bencher as bch
from bencher.example.example_meta import BenchMeta


def example_meta_levels(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    bench = bch.Bench("bench_meta", BenchMeta(), report=report, run_cfg=run_cfg)

    bench.plot_sweep(
        title="Meta Bench Floats",
        description="This uses bencher to show how bencher plots sweeps of floating point variables of increasing dimensionality",
        input_vars=[BenchMeta.param.float_vars.with_sample_values([1, 2, 3])],
        const_vars=[
            BenchMeta.param.categorical_vars.with_const(0),
            BenchMeta.param.level.with_const(4),
        ],
    )

    return bench


if __name__ == "__main__":
    example_meta_levels().report.show()
