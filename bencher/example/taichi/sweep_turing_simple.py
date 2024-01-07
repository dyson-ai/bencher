from turing_pattern import SweepTuring
import bencher as bch


if __name__ == "__main__":
    run_cfg = bch.BenchRunCfg()
    run_cfg.level = 3
    run_cfg.use_sample_cache = False
    run_cfg.run_tag = "sweep_turing_simple"
    bench = SweepTuring().to_bench(run_cfg)

    result_vars = [SweepTuring.param.vid]

    bench.plot_sweep(
        input_vars=[SweepTuring.param.feed], result_vars=result_vars
    )
    
    bench.report.show()
