from turing_pattern import SweepTuring
import bencher as bch


if __name__ == "__main__":
    run_cfg = bch.BenchRunCfg()
    run_cfg.level = 1
    run_cfg.use_sample_cache = True
    run_cfg.run_tag = "best_2"
    bench = SweepTuring().to_bench(run_cfg)

    SweepTuring.param.Du.bounds = None
    SweepTuring.param.Dv.bounds = None
    SweepTuring.param.feed.bounds = None
    SweepTuring.param.kill.bounds = None
    SweepTuring.param.record_volume_vid = True

    res = bench.plot_sweep(
        input_vars=[],
        const_vars=[
            SweepTuring.param.Du.with_const(0.117),
            SweepTuring.param.Dv.with_const(0.0835),
            SweepTuring.param.feed.with_const(0.029),
            SweepTuring.param.kill.with_const(0.065),
        ],
        plot=False,
    )

    bench.report.append(res.to_auto(width=600, height=600))

    bench.report.show()
