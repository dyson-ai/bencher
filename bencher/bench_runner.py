from typing import Protocol, Callable, List
import logging
from bencher.bench_cfg import BenchRunCfg, BenchCfg
from bencher.variables.parametrised_sweep import ParametrizedSweep
from bencher.bencher import Bench
from bencher.bench_report import BenchReport
from copy import deepcopy


class Benchable(Protocol):
    def bench(self, run_cfg: BenchRunCfg, report: BenchReport) -> BenchCfg:
        raise NotImplementedError


class BenchRunner:
    def __init__(
        self,
        bench_class=None,
        run_cfg: BenchRunCfg = BenchRunCfg(),
        publisher: Callable = None,
        report=BenchReport(),
    ) -> None:
        self.run_cfg = BenchRunner.setup_run_cfg(run_cfg)
        self.bench_fns = []
        self.publisher = publisher
        if bench_class is not None:
            self.add_bench(bench_class)
        self.results = []
        self.report = report
        self.servers = []

    @staticmethod
    def setup_run_cfg(run_cfg: BenchRunCfg = BenchRunCfg(), level: int = 1) -> BenchRunCfg:
        run_cfg_out = deepcopy(run_cfg)
        run_cfg_out.use_sample_cache = True
        run_cfg_out.only_hash_tag = True
        run_cfg_out.level = level
        return run_cfg_out

    @staticmethod
    def from_parametrized_sweep(
        class_instance: ParametrizedSweep,
        run_cfg: BenchRunCfg = BenchRunCfg(),
        report: BenchReport = BenchReport(),
    ):
        return Bench(f"bench_{class_instance.name}", class_instance, run_cfg=run_cfg, report=report)

    def add_run(self, bench_fn: Benchable) -> None:
        self.bench_fns.append(bench_fn)

    def add_bench(self, class_instance: ParametrizedSweep) -> None:
        def cb(run_cfg: BenchRunCfg, report: BenchReport) -> BenchCfg:
            bench = BenchRunner.from_parametrized_sweep(
                class_instance, run_cfg=run_cfg, report=report
            )
            return bench.plot_sweep(f"bench_{class_instance.name}")

        self.add_run(cb)

    def run(
        self,
        min_level: int = 2,
        max_level: int = 6,
        level: int = None,
        repeats: int = 1,
        run_cfg: BenchRunCfg = None,
        publish: bool = False,
        debug: bool = True,
        show=False,
        grouped=True,
    ) -> List[BenchCfg]:
        if run_cfg is None:
            run_run_cfg = deepcopy(self.run_cfg)
        else:
            run_run_cfg = BenchRunner.setup_run_cfg(run_cfg)

        if level is not None:
            min_level = level
            max_level = level
        for r in range(1, repeats + 1):
            for lvl in range(min_level, max_level + 1):
                for bch_fn in self.bench_fns:
                    run_lvl = deepcopy(run_run_cfg)
                    run_lvl.level = lvl
                    run_lvl.repeats = r
                    logging.info(f"Running {bch_fn} at level: {lvl} with repeats:{r}")
                    if grouped:
                        res = bch_fn(run_lvl, self.report)
                    else:
                        res = bch_fn(run_lvl, BenchReport())
                    if publish and self.publisher is not None:
                        res.publish(remote_callback=self.publisher, debug=debug)
                    if show:
                        self.servers.append(res.report.show())
                    self.results.append(res)
        return self.results
