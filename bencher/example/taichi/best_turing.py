from turing_pattern import SweepTuring
import bencher as bch


if __name__ == "__main__":
    run_cfg = bch.BenchRunCfg()
    run_cfg.level = 2
    run_cfg.use_sample_cache = False
    run_cfg.run_tag = "best_2"
    bench = SweepTuring().to_bench(run_cfg)

    # bench.plot_sweep(input_vars=["feed","Dv"])
    bench.plot_sweep(input_vars=[SweepTuring.param.Dv],const_vars=[SweepTuring.param.feed.with_const(0.03)],plot=False)

    # SweepTuring.param.Du.bounds = None
    # SweepTuring.param.Dv.bounds = None
    # SweepTuring.param.feed.bounds = None
    # SweepTuring.param.kill.bounds = None
    # SweepTuring.param.record_volume_vid = True

    # v_list=[]
    # v_list.append([0.16,0.8,0.06,0.062])
    # v_list.append([0.175,0.835,0.031,0.059])
    # v_list.append([0.176,0.825,0.06,0.061])
    # v_list.append([0.16,0.85,0.03,0.062])

    # # res = bench.plot_sweep(
    # #         input_vars=[],           
    # #         plot=False,
    # #     )

    # for v in v_list:

    #     # res = bench.plot_sweep(
    #     #     input_vars=[],
    #     #     const_vars=[
    #     #         SweepTuring.param.Du.with_const(0.117),
    #     #         SweepTuring.param.Dv.with_const(0.0835),
    #     #         SweepTuring.param.feed.with_const(0.029),
    #     #         SweepTuring.param.kill.with_const(0.065),
    #     #     ],
    #     #     plot=False,
    #     # )
    #     print("vistli",v)

    #     SweepTuring.param.Du.default = v[0]
    #     SweepTuring.param.Dv.default = v[1]
    #     SweepTuring.param.feed.default = v[2]
    #     SweepTuring.param.kill.default = v[3]

    #     res = bench.plot_sweep("lol",
    #         input_vars=[],
    #         const_vars=[
    #             SweepTuring.param.Du.with_const(v[0]),
    #             SweepTuring.param.Dv.with_const(v[1]),
    #             SweepTuring.param.feed.with_const(v[2]),
    #             SweepTuring.param.kill.with_const(v[3]),
    #         ],
    #         plot=False,
    #     )

    for res in bench.results:
        bench.report.append(res.to_auto(width=600, height=600))

    bench.report.show()
