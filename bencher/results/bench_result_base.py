# from bencher.bench_cfg import BenchCfg


class BenchResultBase:
    def __init__(self, xr_dataset) -> None:
        self.xr_dataset = xr_dataset
