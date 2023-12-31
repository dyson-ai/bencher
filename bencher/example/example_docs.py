import bencher as bch
from bencher.example.example_video import example_video
from bencher.example.example_image import example_image
from bencher.example.meta.example_meta_levels import example_meta_levels
from bencher.example.meta.example_meta_cat import example_meta_cat
from bencher.example.meta.example_meta_float import example_meta_float


def example_docs(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    # b_run = bch.BenchRunner("bench_runner_test", run_cfg=run_cfg)
    # b_run.add_run(example_categorical)
    # b_run.add_run(example_floats)
    # b_run.add_run(example_image)
    # b_run.add_run(example_video)
    # b_run.add_run(example_meta_levels)
    # b_run.add_run(run_levels)
    # b_run.run(level=4, grouped=True, save=True)
    # b_run.shutdown()
    run_cfg.repeats = 1
    run_cfg.level = 2
    example_image(run_cfg, report)
    example_video(run_cfg, report)
    example_meta_cat(report=report)
    example_meta_float(report=report)
    example_meta_levels(report=report)
    # example_meta(run_cfg,report)

    return report


if __name__ == "__main__":
    example_docs().show()
