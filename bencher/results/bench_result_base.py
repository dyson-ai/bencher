import logging
from typing import List, Any, Tuple, Optional
from enum import Enum, auto
import xarray as xr
import holoviews as hv
import numpy as np
from functools import partial
from bencher.utils import int_to_col, color_tuple_to_css

from bencher.variables.parametrised_sweep import ParametrizedSweep
from bencher.variables.results import OptDir
from copy import deepcopy
from bencher.results.optuna_result import OptunaResult
from bencher.variables.results import ResultVar
import panel as pn


# todo add plugins
# https://gist.github.com/dorneanu/cce1cd6711969d581873a88e0257e312
# https://kaleidoescape.github.io/decorated-plugins/


class ReduceType(Enum):
    AUTO = auto()  # automatically determine the best way to reduce the dataset
    SQUEEZE = auto()  # remove any dimensions of length 1
    REDUCE = auto()  # get the mean and std dev of the the "repeat" dimension
    NONE = auto()  # don't reduce


class EmptyContainer:
    """A wrapper for list like containers that only appends if the item is not None"""

    def __init__(self, pane) -> None:
        self.pane = pane

    def append(self, child):
        if child is not None:
            self.pane.append(child)

    def get(self):
        return self.pane if len(self.pane) > 0 else None


class BenchResultBase(OptunaResult):
    def result_samples(self) -> int:
        """The number of samples in the results dataframe"""
        return self.ds.count()

    def to_hv_dataset(
        self, reduce: ReduceType = ReduceType.AUTO, result_var: ResultVar = None
    ) -> hv.Dataset:
        """Generate a holoviews dataset from the xarray dataset.

        Args:
            reduce (ReduceType, optional): Optionally perform reduce options on the dataset.  By default the returned dataset will calculate the mean and standard devation over the "repeat" dimension so that the dataset plays nicely with most of the holoviews plot types.  Reduce.Sqeeze is used if there is only 1 repeat and you want the "reduce" variable removed from the dataset. ReduceType.None returns an unaltered dataset. Defaults to ReduceType.AUTO.

        Returns:
            hv.Dataset: results in the form of a holoviews dataset
        """

        if reduce == ReduceType.AUTO:
            reduce = ReduceType.REDUCE if self.bench_cfg.repeats > 1 else ReduceType.SQUEEZE

        vdims = [r.name for r in self.bench_cfg.result_vars]
        kdims = [i.name for i in self.bench_cfg.all_vars]

        ds = self.ds if result_var is None else self.ds[result_var.name]
        match (reduce):
            case ReduceType.REDUCE:
                # if result_var
                vdims = []
                non_sum = []
                for r in self.bench_cfg.result_vars:
                    if isinstance(r, ResultVar):
                        vdims.append(r.name)
                    else:
                        non_sum.append(r.name)

                ds_num = ds.drop_vars(non_sum)
                return hv.Dataset(ds_num, kdims=kdims, vdims=vdims).reduce(
                    ["repeat"], np.mean, np.std
                )
            case ReduceType.SQUEEZE:
                return hv.Dataset(ds.squeeze(drop=True), vdims=vdims)
            case _:
                return hv.Dataset(ds, kdims=kdims, vdims=vdims)

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

    def title_from_da(self, da: xr.DataArray, result_var: ResultVar, **kwargs):
        if "title" in kwargs:
            return kwargs["title"]

        if isinstance(da, xr.DataArray):
            tit = [da.name]
            for d in da.dims:
                tit.append(d)
        else:
            tit = [result_var.name]
            # data_vars = list(da.data_vars.keys())
            # tit = [data_vars[0]]
            tit.extend(list(da.sizes))

            # tit = list(da.variables)
            # tit = [d for d in da.sizes]

        return " vs ".join(tit)
        # return title

    def get_results_var_list(self, result_var: ParametrizedSweep = None) -> List[ResultVar]:
        return self.bench_cfg.result_vars if result_var is None else [result_var]

    def map_plots(
        self,
        plot_callback: callable,
        result_var: ParametrizedSweep = None,
        row: EmptyContainer = None,
    ) -> Optional[pn.Row]:
        if row is None:
            row = EmptyContainer(pn.Row(name=self.to_plot_title()))
        for rv in self.get_results_var_list(result_var):
            print("RV NAME", rv.name)
            row.append(plot_callback(rv))
        return row.get()

    def map_plot_panes(
        self,
        plot_callback: callable,
        hv_dataset: hv.Dataset = None,
        target_dimension: int = 2,
        result_var: ResultVar = None,
        result_types=None,
        **kwargs,
    ):
        if hv_dataset is None:
            hv_dataset = self.to_hv_dataset()
        row = EmptyContainer(pn.Row())
        for rv in self.get_results_var_list(result_var):
            if result_types is None or isinstance(rv, result_types):
                row.append(
                    self.to_panes_multi_panel(
                        hv_dataset,
                        rv,
                        plot_callback=partial(plot_callback, **kwargs),
                        target_dimension=target_dimension,
                    )
                )
        return row.get()

    def to_panes_multi_panel(
        self,
        hv_dataset: hv.Dataset,
        result_var: ResultVar,
        plot_callback: callable = None,
        target_dimension: int = 1,
        **kwargs,
    ):
        dims = len(hv_dataset.dimensions())
        return self._to_panes_da(
            hv_dataset.data,
            plot_callback=plot_callback,
            target_dimension=target_dimension,
            horizontal=dims <= target_dimension + 1,
            result_var=result_var,
            **kwargs,
        )

    def _to_panes_da(
        self,
        ds: xr.Dataset,
        plot_callback=pn.pane.panel,
        target_dimension=1,
        horizontal=False,
        result_var=None,
        **kwargs,
    ) -> pn.panel:
        # todo, when dealing with time and repeats, add feature to allow custom order of dimension recursion
        ##todo remove recursion
        num_dims = len(ds.sizes)
        # print(f"num_dims: {num_dims}, horizontal: {horizontal}, target: {target_dimension}")
        dims = list(d for d in ds.sizes)

        time_dim_delta = 0
        if self.bench_cfg.over_time:
            time_dim_delta = 0

        if num_dims > (target_dimension + time_dim_delta) and num_dims != 0:
            dim_sel = dims[-1]
            # print(f"selected dim {dim_sel}")

            dim_color = color_tuple_to_css(int_to_col(num_dims - 2, 0.05, 1.0))

            background_col = dim_color
            name = " vs ".join(dims)

            container_args = {"name": name, "styles": {"background": background_col}}
            outer_container = (
                pn.Row(**container_args) if horizontal else pn.Column(**container_args)
            )

            for i in range(ds.sizes[dim_sel]):
                sliced = ds.isel({dim_sel: i})
                label = f"{dim_sel}={sliced.coords[dim_sel].values}"

                panes = self._to_panes_da(
                    sliced,
                    plot_callback=plot_callback,
                    target_dimension=target_dimension,
                    horizontal=len(sliced.sizes) <= target_dimension + 1,
                    result_var=result_var,
                )
                width = num_dims - target_dimension

                container_args = {"name": name, "styles": {"border": f"{width}px solid grey"}}

                if horizontal:
                    inner_container = pn.Column(**container_args)
                    align = ("center", "center")
                else:
                    inner_container = pn.Row(**container_args)
                    align = ("end", "center")

                side = pn.pane.Markdown(f"{label}", align=align)

                inner_container.append(side)
                inner_container.append(panes)
                outer_container.append(inner_container)
        else:
            return plot_callback(da=ds, result_var=result_var, **kwargs)

        return outer_container

    # MAPPING TO LOWER LEVEL BENCHCFG functions so they are available at a top level.
    def to_sweep_summary(self, **kwargs):
        return self.bench_cfg.to_sweep_summary(**kwargs)

    def to_title(self, panel_name: str = None) -> pn.pane.Markdown:
        return self.bench_cfg.to_title(panel_name)

    def to_description(self, width: int = 800) -> pn.pane.Markdown:
        return self.bench_cfg.to_description(width)
