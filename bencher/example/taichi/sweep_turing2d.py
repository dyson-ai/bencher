from turing_pattern import SweepTuring
import bencher as bch


if __name__ == "__main__":
    run_cfg = bch.BenchRunCfg()
    run_cfg.level = 4
    run_cfg.use_sample_cache = True
    run_cfg.run_tag = "sweep_turing2"
    bench = SweepTuring().to_bench(run_cfg)

    result_vars = [SweepTuring.param.vid]
    bench.plot_sweep("turing",input_vars=[SweepTuring.param.feed,SweepTuring.param.Dv],result_vars=result_vars)
    # SweepTuring.param.Dv.default = 0.0825
    bench.plot_sweep("turing",input_vars=[SweepTuring.param.feed,SweepTuring.param.kill])
    bench.report.show()
