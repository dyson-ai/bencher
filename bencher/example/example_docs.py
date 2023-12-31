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

    run_cfg.level = 2
    report = bch.BenchReport()
    example_image(run_cfg, report)
    example_video(run_cfg, report)
    example_meta_cat(run_cfg, report)
    example_meta_float(run_cfg, report)
    run_cfg.level = 4
    example_meta_levels(run_cfg, report)
    # example_meta(run_cfg,report)

    # report.save_index()
    return report


if __name__ == "__main__":
    example_docs().show()
