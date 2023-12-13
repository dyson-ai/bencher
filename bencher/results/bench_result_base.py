# from bencher.bench_cfg import BenchCfg
import pandas as pd
from textwrap import wrap
import numpy as np
from collections.abc import Iterable


class BenchResultBase:
    def __init__(self, bench_cfg) -> None:
        self.bench_cfg = self.wrap_long_time_labels(bench_cfg)  # todo remove
        self.xr_dataset = bench_cfg.ds
        self.input_vars = bench_cfg.input_vars
        self.result_vars = bench_cfg.result_vars
        # self

    def to_xarray(self):
        return self.xr_dataset

    def get_pandas(self, reset_index=True) -> pd.DataFrame:
        """Get the xarray results as a pandas dataframe

        Returns:
            pd.DataFrame: The xarray results array as a pandas dataframe
        """
        ds = self.to_xarray().to_dataframe()
        if reset_index:
            return ds.reset_index()
        return ds

    def to_dataarray(self, squeeze: bool = True):
        var = self.bench_cfg.result_vars[0].name
        xr_dataarray = self.xr_dataset[var]
        if squeeze:
            xr_dataarray = xr_dataarray.squeeze()
        if not isinstance(xr_dataarray["repeat"].values, Iterable):
            xr_dataarray = xr_dataarray.drop_indexes("repeat")
        return xr_dataarray

    def result_samples(self) -> int:
        """The number of samples in the results dataframe"""
        return self.xr_dataset.count()

    def wrap_long_time_labels(self, bench_cfg):
        """Takes a benchCfg and wraps any index labels that are too long to be plotted easily

        Args:
            bench_cfg (BenchCfg):

        Returns:
            BenchCfg: updated config with wrapped labels
        """
        if bench_cfg.over_time:
            if bench_cfg.ds.coords["over_time"].dtype == np.datetime64:
                # plotly catastrophically fails to plot anything with the default long string representation of time, so convert to a shorter time representation
                bench_cfg.ds.coords["over_time"] = [
                    pd.to_datetime(t).strftime("%d-%m-%y %H-%M-%S")
                    for t in bench_cfg.ds.coords.coords["over_time"].values
                ]
                # wrap very long time event labels because otherwise the graphs are unreadable
            if bench_cfg.time_event is not None:
                bench_cfg.ds.coords["over_time"] = [
                    "\n".join(wrap(t, 20)) for t in bench_cfg.ds.coords["over_time"].values
                ]
        return bench_cfg
