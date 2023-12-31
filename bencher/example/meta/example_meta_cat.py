import bencher as bch
from bencher.example.meta.example_meta import BenchMeta


def example_meta_cat(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    bench = BenchMeta().to_bench(run_cfg, report)

    bench.plot_sweep(
        title="Sweeping Categorical Variables",
        input_vars=[
            BenchMeta.param.categorical_vars.with_sample_values([1, 2, 3]),
            BenchMeta.param.sample_with_repeats.with_sample_values([1, 2]),
        ],
        const_vars=[
            BenchMeta.param.float_vars.with_const(0),
        ],
    )

    return bench


if __name__ == "__main__":
    example_meta_cat().report.show()
