from turing_pattern import SweepTuring
import bencher as bch


if __name__ == "__main__":
    run_cfg = bch.BenchRunCfg()
    run_cfg.level = 2
    run_cfg.use_sample_cache = False
    run_cfg.run_tag = "sweep_turing2"
    run_cfg.plot_size=400

    turing = SweepTuring()
    turing.headless = True
    bench = turing.to_bench(run_cfg)

    kwargs = dict(result_vars=["vid","voxel"],const_vars=[["duration",40],["resolution",200]])

    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.feed,SweepTuring.param.Dv],result_vars=result_vars,const_vars=const_vars)
    # SweepTuring.param.Dv.default = 0.0825
    bench.plot_sweep(input_vars=["feed","kill"],**kwargs)
    bench.report.show()
