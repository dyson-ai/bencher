import bencher as bch
from bencher.example.example_meta import BenchMeta


def example_meta_levels(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    bench = bch.Bench("bench_meta", BenchMeta(), report=report, run_cfg=run_cfg)

    bench.plot_sweep(
        title="Using Levels to define sample density",
        description="Sample levels let you perform parameter sweeps without having to decide how many samples to take when defining the class.  If you perform a sweep at level 2, then all the points are reused when sampling at level 3.  The higher levels reuse the points from lower levels to avoid having to recompute potentially expensive samples. The other advantage is that it enables a workflow where you can quickly see the results of the sweep at a low resolution to sense check the code, and then run it at a high level to get the fidelity you want.  When calling a sweep at a high level, you can publish the intermediate lower level results as the computiation continues so that you can track the progress of the computation and end the sweep early when you have sufficient resolution",
        input_vars=[BenchMeta.param.float_vars.with_sample_values([1, 2]), BenchMeta.param.level],
        const_vars=[
            BenchMeta.param.categorical_vars.with_const(0),
        ],
    )

    return bench


if __name__ == "__main__":
    example_meta_levels().report.show()