# from bencher.bench_cfg import BenchCfg #todo enable at very end
import logging
from typing import List, Any, Tuple
from textwrap import wrap
from collections.abc import Iterable

import pandas as pd
import xarray as xr
import numpy as np

from bencher.variables.parametrised_sweep import ParametrizedSweep
from bencher.variables.results import OptDir
from copy import deepcopy

class BenchResultBase:
    def __init__(self, bench_cfg) -> None:
        self.bench_cfg = self.wrap_long_time_labels(bench_cfg)  # todo remove
        self.ds = bench_cfg.ds
        self.input_vars = bench_cfg.input_vars
        self.result_vars = bench_cfg.result_vars
        self.const_vars = bench_cfg.const_vars

    def to_xarray(self) -> xr.Dataset:
        return self.ds

    def get_pandas(self, reset_index=True) -> pd.DataFrame:
        """Get the xarray results as a pandas dataframe

        Returns:
            pd.DataFrame: The xarray results array as a pandas dataframe
        """
        ds = self.to_xarray().to_dataframe()
        if reset_index:
            return ds.reset_index()
        return ds

    def to_dataarray(self, squeeze: bool = True) -> xr.DataArray:
        var = self.bench_cfg.result_vars[0].name
        xr_dataarray = self.ds[var]
        if squeeze:
            xr_dataarray = xr_dataarray.squeeze()
        if not isinstance(xr_dataarray["repeat"].values, Iterable):
            xr_dataarray = xr_dataarray.drop_indexes("repeat")
        return xr_dataarray

    def result_samples(self) -> int:
        """The number of samples in the results dataframe"""
        return self.ds.count()

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

    def get_optimal_vec(
        self,
        result_var: ParametrizedSweep,
        input_vars: List[ParametrizedSweep],
    ) -> List[Any]:
        """Get the optimal values from the sweep as a vector.

        Args:
            result_var (bch.ParametrizedSweep): Optimal values of this result variable
            input_vars (List[bch.ParametrizedSweep]): Define which input vars values are returned in the vector

        Returns:
            List[Any]: A vector of optimal values for the desired input vector
        """

        da = self.get_optimal_value_indices(result_var)
        output = []
        for iv in input_vars:
            if da.coords[iv.name].values.size == 1:
                # https://stackoverflow.com/questions/773030/why-are-0d-arrays-in-numpy-not-considered-scalar
                # use [()] to convert from a 0d numpy array to a scalar
                output.append(da.coords[iv.name].values[()])
            else:
                logging.warning(f"values size: {da.coords[iv.name].values.size}")
                output.append(max(da.coords[iv.name].values[()]))
            logging.info(f"Maximum value of {iv.name}: {output[-1]}")
        return output

    def get_optimal_value_indices(self, result_var: ParametrizedSweep) -> xr.DataArray:
        """Get an xarray mask of the values with the best values found during a parameter sweep

        Args:
            result_var (bch.ParametrizedSweep): Optimal value of this result variable

        Returns:
            xr.DataArray: xarray mask of optimal values
        """
        result_da = self.ds[result_var.name]
        if result_var.direction == OptDir.maximize:
            opt_val = result_da.max()
        else:
            opt_val = result_da.min()
        indicies = result_da.where(result_da == opt_val, drop=True).squeeze()
        logging.info(f"optimal value of {result_var.name}: {opt_val.values}")
        return indicies

    def get_optimal_inputs(
        self, result_var: ParametrizedSweep, keep_existing_consts: bool = True
    ) -> Tuple[ParametrizedSweep, Any]:
        """Get a list of tuples of optimal variable names and value pairs, that can be fed in as constant values to subsequent parameter sweeps

        Args:
            result_var (bch.ParametrizedSweep): Optimal values of this result variable
            keep_existing_consts (bool): Include any const values that were defined as part of the parameter sweep

        Returns:
            Tuple[bch.ParametrizedSweep, Any]: Tuples of variable name and optimal values
        """
        da = self.get_optimal_value_indices(result_var)
        if keep_existing_consts:
            output = deepcopy(self.const_vars)
        else:
            output = []

        for iv in self.input_vars:
            # assert da.coords[iv.name].values.size == (1,)
            if da.coords[iv.name].values.size == 1:
                # https://stackoverflow.com/questions/773030/why-are-0d-arrays-in-numpy-not-considered-scalar
                # use [()] to convert from a 0d numpy array to a scalar
                output.append((iv, da.coords[iv.name].values[()]))
            else:
                logging.warning(f"values size: {da.coords[iv.name].values.size}")
                output.append((iv, max(da.coords[iv.name].values[()])))

            logging.info(f"Maximum value of {iv.name}: {output[-1][1]}")
        return output
