from typing import Protocol, Callable, List
import logging
from bencher.bench_cfg import BenchRunCfg, BenchCfg
from bencher.variables.parametrised_sweep import ParametrizedSweep
from bencher.bencher import Bench

from copy import deepcopy


class Benchable(Protocol):
    def bench(self, run_cfg: BenchRunCfg) -> BenchCfg:
        ...


class BenchRunner:
    def __init__(
        self, bench_class=None, run_cfg: BenchRunCfg = BenchRunCfg(), publisher: Callable = None
    ) -> None:
        self.run_cfg = BenchRunner.setup_run_cfg(run_cfg)
        self.bench_fns = []
        self.publisher = publisher
        if bench_class is not None:
            self.add_bench(bench_class)

    @staticmethod
    def setup_run_cfg(run_cfg: BenchRunCfg = BenchRunCfg(), level: int = 1) -> BenchRunCfg:
        run_cfg_out = deepcopy(run_cfg)
        run_cfg_out.use_sample_cache = True
        run_cfg_out.only_hash_tag = True
        run_cfg_out.level = level
        return run_cfg_out

    @staticmethod
    def from_parametrized_sweep(
        class_instance: ParametrizedSweep, run_cfg: BenchRunCfg = BenchRunCfg()
    ):
        return Bench(f"bench_{class_instance.name}", class_instance, run_cfg=run_cfg)

    def add_run(self, bench_fn: Benchable) -> None:
        self.bench_fns.append(bench_fn)

    def add_bench(self, class_instance: ParametrizedSweep) -> None:
        def cb(run_cfg: BenchRunCfg) -> BenchCfg:
            bench = Bench(f"bench_{class_instance.name}", class_instance, run_cfg=run_cfg)
            return bench.plot_sweep(f"bench_{class_instance.name}")

        self.add_run(cb)

    def run(
        self,
        min_level: int = 2,
        max_level: int = 6,
        run_cfg: BenchRunCfg = None,
        publish: bool = False,
        debug: bool = True,
    ) -> List[BenchCfg]:
        results = []
        if run_cfg is not None:
            run_run_cfg = BenchRunner.setup_run_cfg(run_cfg)
        else:
            run_run_cfg = deepcopy(self.run_cfg)

        for lvl in range(min_level, max_level):
            for bch_fn in self.bench_fns:
                run_lvl = deepcopy(run_run_cfg)
                run_lvl.level = lvl
                logging.info(f"Running {bch_fn} at level: {lvl}")
                res = bch_fn(run_lvl)
                if publish and self.publisher is not None:
                    res.publish(remote_callback=self.publisher, debug=debug)
                results.append(res)
        return results

    # def show(self)
    # self.bench_fns[]
