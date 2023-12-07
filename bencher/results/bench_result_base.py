import xarray as xr


class BenchResultBase:
    def __init__(self, xr_dataset: xr.Dataset,bench_cfg) -> None:
        self.xr_dataset = xr_dataset
        self.bench_cfg = bench_cfg
