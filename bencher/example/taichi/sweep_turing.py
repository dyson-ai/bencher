from turing_pattern import SweepTuring
import bencher as bch


if __name__ == "__main__":
    run_cfg = bch.BenchRunCfg()
    run_cfg.level = 4
    run_cfg.use_sample_cache = True
    run_cfg.run_tag = "sweep_turing_1"
    bench = SweepTuring().to_bench(run_cfg)

    result_vars = [SweepTuring.param.vid]

    bench.plot_sweep(
        input_vars=[SweepTuring.param.Du, SweepTuring.param.Dv], result_vars=result_vars
    )

    SweepTuring.param.Du.bounds = [0.13, 0.19]
    SweepTuring.param.Dv.bounds = [0.08, 0.09]
    run_cfg.level = 4
    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.Du,SweepTuring.param.Dv])

    run_cfg.level = 4

    SweepTuring.param.Du.default = 0.176
    SweepTuring.param.Dv.default = 0.0825
    bench.plot_sweep(
        input_vars=[SweepTuring.param.feed, SweepTuring.param.kill], result_vars=result_vars
    )

    SweepTuring.param.Du.default = 0.176
    SweepTuring.param.Dv.default = 0.0825

    SweepTuring.param.feed.default = 0.03
    SweepTuring.param.kill.default = 0.064

    bench.plot_sweep(
        input_vars=[SweepTuring.param.Du, SweepTuring.param.Dv], result_vars=result_vars
    )

    SweepTuring.param.Du.bounds = None
    SweepTuring.param.Dv.bounds = None
    SweepTuring.param.feed.bounds = None
    SweepTuring.param.kill.bounds = None

    def box(name, center, width):
        var = bch.FloatSweep(default=center, bounds=(center - width, center + width))
        var.name = name
        return var

    # wid = 0.001
    # run_cfg.level = 2
    # bench.plot_sweep(
    #     input_vars=[
    #         box("Du", 0.176, wid),
    #         box("Dv", 0.0825, wid),
    #         box("feed", 0.03, wid),
    #         box("kill", 0.064, wid),
    #     ],
    #     result_vars=result_vars,
    # )
    # bench.plot_sweep(
    #     input_vars=[
    #         box("Du", 0.176, wid),
    #         box("Dv", 0.0825, wid),
    #         box("feed", 0.03, wid),
    #         box("kill", 0.06, 0.001),
    #     ],
    #     result_vars=result_vars,
    # )
    # bench.plot_sweep(
    #     input_vars=[
    #         box("Du", 0.176, wid),
    #         box("Dv", 0.00725, 0.001),
    #         box("feed", 0.03, wid),
    #         box("kill", 0.06, 0.001),
    #     ],
    #     result_vars=result_vars,
    # )

    wid = 0.001
    run_cfg.level = 3

    # bench.plot_sweep(
    #     input_vars=[box("Du", 0.176, wid), box("Dv", 0.00725, 0.001), box("feed", 0.03, wid)],result_vars=result_vars
    # )

    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.feed,SweepTuring.param.Dv])
    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.feed,SweepTuring.param.Dv])

    # SweepTuring.param.Dv.default = 0.0825

    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.feed,SweepTuring.param.kill])

    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.col])

    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.bitrate])
    # bench.report.save_index()
    bench.report.show()
