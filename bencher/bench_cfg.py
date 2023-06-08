from __future__ import annotations
import param
from typing import List, Callable, Tuple, Any
from bencher.bench_vars import (
    TimeSnapshot,
    TimeEvent,
    describe_variable,
    OptDir,
)
import bencher as bch
import logging
import argparse
from distutils.util import strtobool
import copy
import xarray as xr


def to_filename(
    param_cfg: param.Parameterized, param_list: list[str] = None, exclude_params: list[str] = None
) -> str:
    """given a parametrized class, generate a filename based on some of the parameter properties

    Args:
        param_cfg (param.Parameterized): any parametrized class
        param_list (list[str], optional): params to include in the filename. Defaults to None.
        exclude_params (list[str], optional): params to exclude from the filename. Defaults to None.

    Returns:
        str: a filename string
    """

    if exclude_params is None:
        exclude_params = []
    # param_cfg.get_param_values()
    if param_list is None:
        changed_params = param_cfg.param.values(onlychanged=True)
    else:
        params_dict = param_cfg.param.values()
        changed_params = {}
        for p in param_list:
            changed_params[p] = params_dict[p]

    # by default we don't want the name as part of the filename (because it is unquie per instance), but during debugging the hashing its useful to be able to turn on name as part of the timename to isolate what parts of the filename are not unique
    output = [f"{param_cfg.name},"]
    output = []
    for k, v in changed_params.items():
        if k not in exclude_params:
            output.append(f"{k}={v.__repr__()},")
    return "".join(output)[:-1].replace("'", "")  # remove trailing comma


class PltCfgBase(param.Parameterized):
    """A base class that contains plotting parameters shared by seaborn and xarray"""

    x: str = param.String(None, doc="the x parameter for seaborn and xarray plotting functions")
    y: str = param.String(None, doc="the y parameter for seaborn and xarray plotting functions")
    z: str = param.String(None, doc="the z parameter for xarray plotting functions")
    hue: str = param.String(None, doc="the hue parameter for seaborn and xarray plotting functions")

    row: str = param.String(None, doc="the row parameter for seaborn and xarray plotting functions")
    col: str = param.String(None, doc="the col parameter for seaborn and xarray plotting functions")

    num_rows: int = param.Integer(1, doc="The number of rows in the facetgrid")
    num_cols: int = param.Integer(1, doc="The number of cols in the facetgrid")

    kind: str = param.String(None, doc="the 'kind' of plot, ie barplot, lineplot, scatter etc")
    marker: str = param.String(None, doc="The marker to use when plotting")

    cmap = param.String(None, doc="colormap type")

    plot_callback_sns: Callable = None
    plot_callback_xra: Callable = None
    plot_callback: Callable = None

    xlabel: str = param.String(None, doc="The label for the x-axis")
    ylabel: str = param.String(None, doc="The label for the y-axis")
    zlabel: str = param.String(None, doc="The label for the z-axis")

    title: str = param.String(None, doc="The title of the graph")

    def as_dict(self, include_params: List[str] = None, exclude_params: List[str] = None) -> dict:
        """Return this class as dictionary to pass to plotting functions but exclude parameters that are not expected by those functions

        Args:
            include_params (List[str], optional): a list of property names to include. Defaults to None.
            exclude_params (List[str], optional): a list of property names to exclude. Defaults to None.

        Returns:
            dict: a dictionary of plotting arguments
        """
        all_params = self.param.values()
        all_params.pop("name")

        output = {}
        if include_params is not None:
            for i in include_params:
                output[i] = all_params[i]
        else:
            output = all_params

        if exclude_params is not None:
            for e in exclude_params:
                output.pop(e)

        return output

    def as_sns_args(self) -> dict:
        return self.as_dict(include_params=["x", "y", "hue", "row", "col", "kind", "marker"])

    def as_xra_args(self) -> dict:
        return self.as_dict(include_params=["x", "y", "hue", "row", "col", "cmap"])

    def as_filename(self) -> str:
        """generate a unique filename based on the plotting configuration

        Returns:
            str: filename
        """
        return to_filename(self, exclude_params=["marker", "xlabel", "ylabel", "title"])


class PltCntCfg(param.Parameterized):
    """Plot Count Config"""

    float_vars = param.List(doc="A list of float vars in order of plotting, x then y")
    float_cnt = param.Integer(0, doc="The number of float variables to plot")
    cat_vars = param.List(doc="A list of categorical values to plot in order hue,row,col")
    cat_cnt = param.Integer(0, doc="The number of cat variables")


class BenchPlotSrvCfg(param.Parameterized):
    port: int = param.Integer(None, doc="The port to launch panel with")


class BenchRunCfg(BenchPlotSrvCfg):
    """A Class to store options for how to run a benchmark parameter sweep"""

    repeats: bool = param.Integer(1, doc="The number of times to sample the inputs")

    over_time: bool = param.Boolean(
        False,
        doc="If true each time the function is called it will plot a timeseries of historical and the latest result.",
    )

    debug: bool = param.Boolean(
        False, doc="Debug the sampling faster by reducing the dimension sampling resolution"
    )

    use_optuna: bool = param.Boolean(
        False,
        doc="show optuna plots",
    )

    print_bench_inputs: bool = param.Boolean(
        True, doc="Print the inputs to the benchmark function every time it is called"
    )

    clear_history: bool = param.Boolean(False, doc="Clear historical results")

    print_pandas: bool = param.Boolean(
        False, doc="Print a pandas summary of the results to the console."
    )

    print_xarray: bool = param.Boolean(
        False, doc="Print an xarray summary of the results to the console"
    )

    serve_pandas: bool = param.Boolean(
        True,
        doc="Serve a pandas summary on the results webpage.  If you have a large dataset consider setting this to false if the page loading is slow",
    )

    serve_xarray: bool = param.Boolean(
        True,
        doc="Serve an xarray summary on the results webpage. If you have a large dataset consider setting this to false if the page loading is slow",
    )

    auto_plot: bool = param.Boolean(
        True, doc=" Automaticlly dedeuce the best type of plot for the results."
    )

    raise_duplicate_exception: bool = param.Boolean(False, doc=" Used to debug unique plot names.")

    use_cache: bool = param.Boolean(
        False,
        doc=" If true, before calling the objective function, the sampler will check if these inputs have been calculated before and if so load them from the cache. Beware depending on how you change code in the objective function, the cache could provide values that are not correct.",
    )

    clear_cache: bool = param.Boolean(
        False, doc=" Clear the cache of saved input->output mappings."
    )

    only_plot: bool = param.Boolean(
        False, doc="Do not attempt to calculate benchmarks if no results are found in the cache"
    )

    save_fig: bool = param.Boolean(False, doc="Optionally save a png of each figure")
    use_holoview: bool = param.Boolean(False, doc="Use holoview for plotting")

    nightly: bool = param.Boolean(
        False, doc="Run a more extensive set of tests for a nightly benchmark"
    )

    time_event: str = param.String(
        None,
        doc="A string representation of a sequence over time, i.e. datetime, pull request number, or run number",
    )

    headless: bool = param.Boolean(False, doc="Run the benchmarks headlessly")

    @staticmethod
    def from_cmd_line() -> BenchRunCfg:
        """create a BenchRunCfg by parsing command line arguments

        Returns:
            parsed args: parsed args
        """

        parser = argparse.ArgumentParser(description="benchmark")

        parser.add_argument(
            "--use-cache",
            action="store_true",
            help=BenchRunCfg.param.use_cache.doc,
        )

        parser.add_argument(
            "--only-plot",
            action="store_true",
            help=BenchRunCfg.param.only_plot.doc,
        )

        parser.add_argument(
            "--port",
            type=int,
            help=BenchRunCfg.param.port.doc,
        )

        parser.add_argument(
            "--nightly",
            type=lambda b: bool(strtobool(b)),
            nargs="?",
            const=False,
            default=False,
            help="turn on nightly benchmarking",
        )

        parser.add_argument(
            "--time_event",
            type=str,
            default=BenchRunCfg.param.time_event.default,
            help=BenchRunCfg.param.time_event.doc,
        )

        parser.add_argument(
            "--repeats",
            type=int,
            default=BenchRunCfg.param.repeats.default,
            help=BenchRunCfg.param.repeats.doc,
        )

        return BenchRunCfg(**vars(parser.parse_args()))

   


class BenchCfg(BenchRunCfg):
    """A class for storing the arguments to configure a benchmark protocol  If the inputs variables are the same the class should return the same hash and same filename.  This is so that historical data can be referenced and ensures that the generated plots are unique per benchmark"""

    input_vars = param.List(
        default=None,
        doc="A list of ParameterizedSweep variables to perform a parameter sweep over",
    )
    result_vars = param.List(
        default=None,
        doc="A list of ParameterizedSweep results collect and plot.",
    )

    const_vars = param.List(
        default=None,
        doc="Variables to keep constant but are different from the default value",
    )

    meta_vars = param.List(
        default=None,
        doc="Meta variables such as recording time and repeat id",
    )
    all_vars = param.List(
        default=None,
        doc="Stores a list of both the input_vars and meta_vars that are used to define a unique hash for the input",
    )
    iv_time = param.List(
        default=[],
        class_=TimeSnapshot | TimeEvent,
        doc="A parameter to represent the sampling the same inputs over time as a scalar type",
    )

    iv_time_event = param.List(
        default=[],
        class_=TimeEvent,
        doc="A parameter to represent the sampling the same inputs over time as a discrete type",
    )

    over_time: param.Boolean(
        False, doc="A parameter to control whether the function is sampled over time"
    )
    name: str = param.String(None, doc="The name of the benchmarkCfg")
    title: str = param.String(None, doc="The title of the benchmark")
    raise_duplicate_exception: str = param.Boolean(
        False, doc="Use this while debugging if filename generation is unique"
    )
    bench_name: str = param.String(
        None, doc="The name of the benchmark and the name of the save folder"
    )
    description: str = param.String(
        None, doc="A place to store a longer description of the function of the benchmark"
    )
    post_description: str = param.String(None, doc="A place to comment on the output of the graphs")

    has_results: bool = param.Boolean(
        False,
        doc="If this config has results, true, otherwise used to store titles and other bench metadata",
    )

    ds = []

    def __hash__(self):
        """override the default hash function becuase the default hash function does not return the same value for the same inputs.  It references internal variables that are unique per instance of BenchCfg"""
        all_vars = self.input_vars + self.result_vars + self.const_vars

        hash_val = hash(
            (
                hash(str(self.bench_name)),
                hash(str(self.title)),
                hash(self.over_time),
                hash(self.repeats),  # needed so that the historical xarray arrays are the same size
                hash(self.debug),
            )
        )
        for v in all_vars:
            hash_val = hash((hash_val, hash(v)))

        return hash_val

    def as_filename(self) -> str:
        """Generate a unique filename for this BenchCfg"""
        strs = []
        strs.append("rv:")
        for r in self.result_vars:
            strs.append(f"{r.name},")
        strs.append(f"repeats={self.repeats},over_time={self.over_time}")
        return "".join(strs)

    def get_optimal_value_indices(self, result_var: bch.ParametrizedOutput) -> xr.DataArray:
        """Get an xarray mask of the values with the best values found during a parameter sweep

        Args:
            result_var (bch.ParametrizedOutput): Optimal value of this result variable

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
        self, result_var: bch.ParametrizedOutput, keep_existing_consts: bool = True
    ) -> Tuple[bch.ParametrizedSweep, Any]:
        """Get a list of tuples of optimal variable names and value pairs, that can be fed in as constant values to subsequent parameter sweeps

        Args:
            result_var (bch.ParametrizedOutput): Optimal values of this result variable
            keep_existing_consts (bool): Include any const values that were defined as part of the parameter sweep

        Returns:
            Tuple[bch.ParametrizedSweep, Any]: Tuples of variable name and optimal values
        """
        da = self.get_optimal_value_indices(result_var)
        if keep_existing_consts:
            output = copy.deepcopy(self.const_vars)
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

    def get_optimal_vec(
        self, result_var: bch.ParametrizedOutput, input_vars: List[bch.ParametrizedSweep]
    ) -> List[Any]:
        """Get the optimal values from the sweep as a vector.

        Args:
            result_var (bch.ParametrizedOutput): Optimal values of this result variable
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


def describe_benchmark(bench_cfg: BenchCfg) -> str:
    """Generate a string summary of the inputs and results from a BenchCfg

    Args:
        bench_cfg (BenchCfg): BenchCfg to generate a summary of

    Returns:
        str: summary of BenchCfg
    """
    benchmark_sampling_str = ["````text"]
    benchmark_sampling_str.append("")
    benchmark_sampling_str.append("Input Variables:")
    for iv in bench_cfg.input_vars:
        benchmark_sampling_str.extend(describe_variable(iv, bench_cfg.debug, True))

    if bench_cfg.const_vars:
        benchmark_sampling_str.append("\nConstants:")
        for cv in bench_cfg.const_vars:
            c = cv[0]
            benchmark_sampling_str.extend(
                [f"\t{c.name}: \n\t\tvalue: {cv[1]}\n\t\tunits: {c.units}\n\t\tdocs: {c.doc}"]
            )

    print_meta = True
    if len(bench_cfg.meta_vars) == 1:
        mv = bench_cfg.meta_vars[0]
        if mv.name == "repeat" and mv.samples == 1:
            print_meta = False

    if print_meta:
        benchmark_sampling_str.append("\nMeta Variables:")
        for mv in bench_cfg.meta_vars:
            benchmark_sampling_str.extend(describe_variable(mv, bench_cfg.debug, True))

    benchmark_sampling_str.append("\nResult Variables:")
    for rv in bench_cfg.result_vars:
        benchmark_sampling_str.extend(describe_variable(rv, bench_cfg.debug, False))

    benchmark_sampling_str.append("````")

    # TODO enable printing of const variables
    # benchmark_sampling_str.append("Constant Inputs:")
    # for cv in bench_cfg.const_vars:
    #     benchmark_sampling_str.extend(describe_variable(cv, bench_cfg.debug, False))

    benchmark_sampling_str = "\n".join(benchmark_sampling_str)
    return benchmark_sampling_str


class DimsCfg:
    """A class to store data about the sampling and result dimensions"""

    def __init__(self, bench_cfg: BenchCfg) -> None:

        self.dims_name = [i.name for i in bench_cfg.all_vars]
        self.dim_ranges = [i.values(bench_cfg.debug) for i in bench_cfg.all_vars]
        self.dims_size = [len(p) for p in self.dim_ranges]
        self.dim_ranges_index = [list(range(i)) for i in self.dims_size]
        self.dim_ranges_str = [f"{s}\n" for s in self.dim_ranges]
        self.coords = dict(zip(self.dims_name, self.dim_ranges))

        logging.debug(f"dims_name: {self.dims_name}")
        logging.debug(f"dim_ranges {self.dim_ranges_str}")
        logging.debug(f"dim_ranges_index {self.dim_ranges_index}")
        logging.debug(f"coords: {self.coords}")
