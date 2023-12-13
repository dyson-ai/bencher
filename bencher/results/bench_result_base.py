# from bencher.bench_cfg import BenchCfg
from pandas import DataFrame


class BenchResultBase:
    def __init__(self, bench_cfg) -> None:
        self.bench_cfg = bench_cfg  # todo remove
        self.xr_dataset = bench_cfg.ds

    def to_xarray(self):
        return self.xr_dataset

    def get_pandas(self, reset_index=True) -> DataFrame:
        """Get the xarray results as a pandas dataframe

        Returns:
            pd.DataFrame: The xarray results array as a pandas dataframe
        """
        ds = self.to_xarray().to_dataframe()
        if reset_index:
            return ds.reset_index()
        return ds

    def result_samples(self) -> int:
        """The number of samples in the results dataframe"""
        return self.xr_dataset.count()
