import bencher as bch
from bencher.example.taichi.turing_pattern import SweepTuring

if __name__ == "__main__":
    run_cfg = bch.BenchRunCfg()
    run_cfg.level = 2
    run_cfg.use_sample_cache = False
    bench = SweepTuring().to_bench(run_cfg)

    SweepTuring.param.Du.bounds = [0.13, 0.19]

    SweepTuring.param.record_volume_vid.default = True

    bench.plot_sweep("turing", input_vars=[SweepTuring.param.feed])
    bench.report.show()
