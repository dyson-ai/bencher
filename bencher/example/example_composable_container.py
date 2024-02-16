import bencher as bch
import numpy as np
import math
import matplotlib.pyplot as plt
from example_image import BenchPolygons


class BenchComposableContainerImage(BenchPolygons):

    compose_method = bch.EnumSweep(bch.ComposeType)
    labels = bch.BoolSweep()
    num_frames = bch.IntSweep(default=5, bounds=[1, 10])
    polygon_vid = bch.ResultVideo()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        var_name = None
        var_value = None

        if self.labels:
            var_name = "sides"
            var_value = self.sides
        vr = bch.ComposableContainerVideo(
            target_duration=1,
            compose_method=self.compose_method,
            var_name=var_name,
            var_value=var_value,
        )
        for i in range(5):
            res = super().__call__(start_angle=i)
            vr.append(res["polygon"])
        self.polygon_vid = vr.to_video()
        return self.get_results_values_as_dict()


class BenchComposableContainerVideo(BenchComposableContainerImage):

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        vr = bch.ComposableContainerVideo(target_duration=1, compose_method=self.compose_method)
        for i in range(3, 5):
            res = super().__call__(compose_method=bch.ComposeType.sequence, sides=i)
            vr.append(res["polygon_vid"])

        self.polygon_vid = vr.to_video()
        return self.get_results_values_as_dict()


def example_composable_container_image(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    bench = BenchComposableContainerImage().to_bench(run_cfg, report)
    bench.result_vars = ["polygon_vid"]
    bench.add_plot_callback(bch.BenchResult.to_panes)
    bench.plot_sweep(input_vars=["compose_method", "labels"])
    return bench


def example_composable_container_video(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    bench = BenchComposableContainerVideo().to_bench(run_cfg, report)
    bench.result_vars = ["polygon_vid"]
    bench.add_plot_callback(bch.BenchResult.to_panes)
    bench.plot_sweep(input_vars=["compose_method", "labels"])
    return bench


if __name__ == "__main__":
    ex_run_cfg = bch.BenchRunCfg()
    ex_run_cfg.use_sample_cache = False
    # ex_run_cfg.level = 2
    report = bch.BenchReport()
    example_composable_container_image(ex_run_cfg, report=report)
    example_composable_container_video(ex_run_cfg, report=report)
    report.show()
