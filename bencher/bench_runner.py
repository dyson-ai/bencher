from typing import Protocol

from bencher.bench_cfg import BenchRunCfg, BenchCfg
from copy import deepcopy


class Benchable(Protocol):
    def bench(run_cfg: BenchRunCfg) -> BenchCfg:
        ...


class BenchRunner:
    def __init__(self, run_cfg: BenchRunCfg = BenchRunCfg(), publisher=None) -> None:
        self.run_cfg = BenchRunner.setup_run_cfg(run_cfg)

        self.bench_fns = []
        self.publisher = publisher

    @staticmethod
    def setup_run_cfg(run_cfg: BenchRunCfg = BenchRunCfg(), level=1):
        run_cfg_out = deepcopy(run_cfg)
        run_cfg_out.use_sample_cache = True
        run_cfg_out.only_hash_tag = True
        run_cfg.level = level
        return run_cfg_out

    # @staticmethod
    # def gen_run_cfg_from_level(level):

    #     return BenchRunner.setup_run_cfg()

    def add_run(self, bench_fn: Benchable):
        self.bench_fns.append(bench_fn)

    def run(
        self, min_level=1, max_level=4, run_cfg: BenchRunCfg = None, publish: bool = False
    ) -> None:
        if run_cfg is not None:
            run_run_cfg = BenchRunner.setup_run_cfg(run_cfg)
        else:
            run_run_cfg = deepcopy(self.run_cfg)

        for lvl in range(min_level, max_level):
            for b in self.bench_fns:
                run_lvl = deepcopy(run_run_cfg)
                run_lvl.level = lvl
                b.bench(run_lvl)
            # if publish:
            # res.publish

    # def show(self):
