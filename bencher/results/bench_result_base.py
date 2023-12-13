from bencher.bench_cfg import BenchCfg


class BenchResultBase:
    def __init__(self, bench_cfg: BenchCfg) -> None:
        self.bench_cfg = bench_cfg
        self.xr_dataset = bench_cfg.ds
