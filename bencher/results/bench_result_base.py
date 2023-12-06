import xarray as xr


class BenchResultBase:
    def __init__(self, xr_dataset: xr.Dataset) -> None:
        self.xr_dataset = xr_dataset
