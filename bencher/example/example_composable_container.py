import bencher as bch
import numpy as np
import math
import matplotlib.pyplot as plt
from example_image import BenchPolygons


class BenchComposableContainerVideo(BenchPolygons):

    compose_method = bch.EnumSweep(bch.ComposeType)
    polygon_vid = bch.ResultVideo()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        vr = bch.ComposableContainerVideo(target_duration=1, compose_method=self.compose_method)
        for i in range(10):
            res = super().__call__(start_angle=i)
            vr.append(res["polygon"])
        self.polygon_vid = vr.to_video()
        return self.get_results_values_as_dict()


def example_composable_container(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    bench = BenchComposableContainerVideo().to_bench(run_cfg, report)
    bench.result_vars = ["polygon_vid"]
    # bench.const_vars = dict(compose_method=bch.ComposeType.right)
    bench.add_plot_callback(bch.BenchResult.to_panes)

    bench.plot_sweep(input_vars=["compose_method"])
    # bench.plot_sweep(input_vars=["radius", "sides"])
    # bench.plot_sweep(input_vars=["radius", "sides", "linewidth"])
    # bench.plot_sweep(input_vars=["radius", "sides", "linewidth", "color"])

    return bench


if __name__ == "__main__":
    ex_run_cfg = bch.BenchRunCfg()
    ex_run_cfg.use_sample_cache = False
    # ex_run_cfg.level = 2
    example_composable_container(ex_run_cfg).report.show()
