import logging
from typing import List, Any, Tuple, Optional
from collections.abc import Iterable

import xarray as xr

from bencher.variables.parametrised_sweep import ParametrizedSweep
from bencher.variables.results import OptDir
from copy import deepcopy
from bencher.results.optuna_result import OptunaResult
from bencher.variables.results import ResultVar
import panel as pn


# todo add plugins
# https://gist.github.com/dorneanu/cce1cd6711969d581873a88e0257e312
# https://kaleidoescape.github.io/decorated-plugins/


class BenchResultBase(OptunaResult):
    def to_dataarray(self, result_var: ResultVar, squeeze: bool = True) -> xr.DataArray:
        var = result_var.name
        xr_dataarray = self.ds[var]
        if squeeze:
            xr_dataarray = xr_dataarray.squeeze()
        if not isinstance(xr_dataarray["repeat"].values, Iterable):
            xr_dataarray = xr_dataarray.drop_indexes("repeat")
        return xr_dataarray

    def result_samples(self) -> int:
        """The number of samples in the results dataframe"""
        return self.ds.count()

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
            output = deepcopy(self.bench_cfg.const_vars)
        else:
            output = []

        for iv in self.bench_cfg.input_vars:
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

    def describe_sweep(self):
        return self.bench_cfg.describe_sweep()

    def get_best_holomap(self, name: str = None):
        return self.get_hmap(name)[self.get_best_trial_params(True)]

    def get_hmap(self, name: str = None):
        try:
            if name is None:
                name = self.result_hmaps[0].name
                print(name)
            if name in self.hmaps:
                return self.hmaps[name]
        except Exception as e:
            raise RuntimeError(
                "You are trying to plot a holomap result but it is not in the result_vars list.  Add the holomap to the result_vars list"
            ) from e
        return None

    def to_plot_title(self) -> str:
        if len(self.bench_cfg.input_vars) > 0 and len(self.bench_cfg.result_vars) > 0:
            return f"{self.bench_cfg.result_vars[0].name} vs {self.bench_cfg.input_vars[0].name}"            
        return ""
    
    def to_title(self,result_var:ResultVar):
        title= f"{result_vars[0].name}"
        for iv in self.bench_cfg.input_vars:
            title += f" vs {iv.name}"
        return title

    def get_results_var_list(self, result_var: ParametrizedSweep = None) -> List[ResultVar]:
        return self.bench_cfg.result_vars if result_var is None else [result_var]
        # return pn.Row(*[self.to_volume_single(rv) for rv in rvs])

    def map_plots(
        self, plot_callback: callable, result_var: ParametrizedSweep = None, row: pn.Row = None
    ) -> Optional[pn.Row]:
        if row is None:
            row = pn.Column(name=self.to_plot_title())
        for rv in self.get_results_var_list(result_var):
            print("RV NAME", rv.name)
            plot_result = plot_callback(rv)
            if plot_result is not None:
                row.append(plot_result)
        return row if len(row) > 0 else None

    # MAPPING TO LOWER LEVEL BENCHCFG functions so they are available at a top level.
    def to_sweep_summary(self):
        return self.bench_cfg.to_sweep_summary()

    def to_title(self, panel_name: str = None) -> pn.pane.Markdown:
        return self.bench_cfg.to_title(panel_name)

    def to_description(self, width: int = 800) -> pn.pane.Markdown:
        return self.bench_cfg.to_description(width)
