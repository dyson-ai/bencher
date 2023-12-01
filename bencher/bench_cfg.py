from __future__ import annotations

import argparse
import copy
import logging
from collections import defaultdict

from typing import Any, Callable, List, Tuple

import param
import xarray as xr
from pandas import DataFrame
from str2bool import str2bool
import holoviews as hv
import numpy as np
import panel as pn


import bencher as bch
from bencher.variables.sweep_base import hash_sha1, describe_variable
from bencher.variables.time import TimeSnapshot, TimeEvent
from bencher.variables.results import OptDir
from bencher.utils import hmap_canonical_input, get_nearest_coords
from bencher.job import Executors
from enum import Enum, auto
from datetime import datetime


class ReduceType(Enum):
    AUTO = auto()
    SQUEEZE = auto()
    REDUCE = auto()
    NONE = auto()


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

    width: int = param.Integer(700, doc="Width of the plot in pixels")
    height: int = param.Integer(700, doc="Height of the plot in pixels")

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
        return self.as_dict(include_params=["x", "y", "hue", "row", "col", "kind"])


class PltCntCfg(param.Parameterized):
    """Plot Count Config"""

    float_vars = param.List(doc="A list of float vars in order of plotting, x then y")
    float_cnt = param.Integer(0, doc="The number of float variables to plot")
    cat_vars = param.List(doc="A list of categorical values to plot in order hue,row,col")
    cat_cnt = param.Integer(0, doc="The number of cat variables")
    vector_len = param.Integer(1, doc="The vector length of the return variable , scalars = len 1")
    result_vars = param.Integer(1, doc="The number result variables to plot")


class BenchPlotSrvCfg(param.Parameterized):
    port: int = param.Integer(None, doc="The port to launch panel with")
    allow_ws_origin = param.Boolean(
        False,
        doc="Add the port to the whilelist, (warning will disable remote access if set to true)",
    )
    show: bool = param.Boolean(True, doc="Open the served page in a web browser")


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

    use_optuna: bool = param.Boolean(False, doc="show optuna plots")

    summarise_constant_inputs = param.Boolean(
        True, doc="Print the inputs that are kept constant when describing the sweep parameters"
    )

    print_bench_inputs: bool = param.Boolean(
        True, doc="Print the inputs to the benchmark function every time it is called"
    )

    print_bench_results: bool = param.Boolean(
        True, doc="Print the results of the benchmark function every time it is called"
    )

    clear_history: bool = param.Boolean(False, doc="Clear historical results")

    print_pandas: bool = param.Boolean(
        False, doc="Print a pandas summary of the results to the console."
    )

    print_xarray: bool = param.Boolean(
        False, doc="Print an xarray summary of the results to the console"
    )

    serve_pandas: bool = param.Boolean(
        False,
        doc="Serve a pandas summary on the results webpage.  If you have a large dataset consider setting this to false if the page loading is slow",
    )

    serve_pandas_flat: bool = param.Boolean(
        True,
        doc="Serve a flattend pandas summary on the results webpage.  If you have a large dataset consider setting this to false if the page loading is slow",
    )

    serve_xarray: bool = param.Boolean(
        False,
        doc="Serve an xarray summary on the results webpage. If you have a large dataset consider setting this to false if the page loading is slow",
    )

    auto_plot: bool = param.Boolean(
        True, doc=" Automaticlly dedeuce the best type of plot for the results."
    )

    raise_duplicate_exception: bool = param.Boolean(False, doc=" Used to debug unique plot names.")

    use_cache: bool = param.Boolean(
        False,
        doc="This is a benchmark level cache that stores the results of a fully completed benchmark. At the end of a benchmark the values are added to the cache but are not if the benchmark does not complete.  If you want to cache values during the benchmark you need to use the use_sample_cache option. Beware that depending on how you change code in the objective function, the cache could provide values that are not correct.",
    )

    clear_cache: bool = param.Boolean(
        False, doc=" Clear the cache of saved input->output mappings."
    )

    use_sample_cache: bool = param.Boolean(
        False,
        doc="If true, every time the benchmark function is called, bencher will check if that value has been calculated before and if so load the from the cache.  Note that the sample level cache is different from the benchmark level cache which only caches the aggregate of all the results at the end of the benchmark. This cache lets you stop a benchmark halfway through and continue. However, beware that depending on how you change code in the objective function, the cache could provide values that are not correct.",
    )

    only_hash_tag: bool = param.Boolean(
        False,
        doc="By default when checking if a sample has been calculated before it includes the hash of the greater benchmarking context.  This is safer because it means that data generated from one benchmark will not affect data from another benchmark.  However, if you are careful it can be more flexible to ignore which benchmark generated the data and only use the tag hash to check if that data has been calculated before. ie, you can create two benchmarks that sample a subset of the problem during exploration and give them the same tag, and then afterwards create a larger benchmark that covers the cases you already explored.  If this value is true, the combined benchmark will use any data from other benchmarks with the same tag.",
    )

    clear_sample_cache: bool = param.Boolean(
        False,
        doc="Clears the per-sample cache.  Use this if you get unexpected behavior.  The per_sample cache is tagged by the specific benchmark it was sampled from. So clearing the cache of one benchmark will not clear the cache of other benchmarks.",
    )

    overwrite_sample_cache: bool = param.Boolean(
        False,
        doc="If True, recalculate the value and overwrite the value stored in the sample cache",
    )

    only_plot: bool = param.Boolean(
        False, doc="Do not attempt to calculate benchmarks if no results are found in the cache"
    )

    use_holoview: bool = param.Boolean(False, doc="Use holoview for plotting")

    nightly: bool = param.Boolean(
        False, doc="Run a more extensive set of tests for a nightly benchmark"
    )

    time_event: str = param.String(
        None,
        doc="A string representation of a sequence over time, i.e. datetime, pull request number, or run number",
    )

    headless: bool = param.Boolean(False, doc="Run the benchmarks headlessly")

    render_plotly = param.Boolean(
        True,
        doc="Plotly and Bokeh don't play nicely together, so by default pre-render plotly figures to a non dynamic version so that bokeh plots correctly.  If you want interactive 3D graphs, set this to true but be aware that your 2D interactive graphs will probalby stop working.",
    )

    level = param.Integer(
        default=0,
        bounds=[0, 12],
        doc="The level parameter is a method of defining the number samples to sweep over in a variable agnostic way, i.e you don't need to specficy the number of samples for each variable as they are calculated dynamically from the sampling level.  See example_level.py for more information.",
    )

    run_tag = param.String(
        default="",
        doc="Define a tag for a run to isolate the results stored in the cache from other runs",
    )

    run_date = param.Date(
        default=datetime.now(),
        doc="The date the bench run was performed",
    )

    # parallel = param.Boolean(
    #     default=False,
    #     doc="Run the sweep in parallel.  Warning! You need to make sure your code is threadsafe before using this option",
    # )

    executor = param.Selector(
        objects=list(Executors),
        doc="The function can be run serially or in parallel with different futures executors",
    )

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
            type=lambda b: bool(str2bool(b)),
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

    result_hmaps = param.List(default=None, doc="a list of holomap results")

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
        None,
        doc="A place to store a longer description of the function of the benchmark",
    )
    post_description: str = param.String(None, doc="A place to comment on the output of the graphs")

    has_results: bool = param.Boolean(
        False,
        doc="If this config has results, true, otherwise used to store titles and other bench metadata",
    )

    pass_repeat: bool = param.Boolean(
        False,
        doc="By default do not pass the kwarg 'repeat' to the benchmark function.  Set to true if you want the benchmark function to be passed the repeat number",
    )

    tag: str = param.String(
        "",
        doc="Use tags to group different benchmarks together. By default benchmarks are considered distinct from eachother and are identified by the hash of their name and inputs, constants and results and tag, but you can optionally change the hash value to only depend on the tag.  This way you can have multiple unrelated benchmarks share values with eachother based only on the tag value.",
    )

    hash_value: str = param.String(
        "",
        doc="store the hash value of the config to avoid having to hash multiple times",
    )

    def __init__(self, **params):
        super().__init__(**params)
        self.studies = []
        self.ds = xr.Dataset()
        self.plot_lib = None
        # self.hmap = {}
        self.hmaps = defaultdict(dict)
        self.hmap_kdims = None
        self.iv_repeat = None

    def hash_persistent(self, include_repeats) -> str:
        """override the default hash function becuase the default hash function does not return the same value for the same inputs.  It references internal variables that are unique per instance of BenchCfg

        Args:
            include_repeats (bool) : by default include repeats as part of the hash execpt with using the sample cache
        """

        if include_repeats:
            # needed so that the historical xarray arrays are the same size
            repeats_hash = hash_sha1(self.repeats)
        else:
            repeats_hash = 0

        hash_val = hash_sha1(
            (
                hash_sha1(str(self.bench_name)),
                hash_sha1(str(self.title)),
                hash_sha1(self.over_time),
                repeats_hash,
                hash_sha1(self.debug),
                hash_sha1(self.tag),
            )
        )
        all_vars = self.input_vars + self.result_vars
        for v in all_vars:
            hash_val = hash_sha1((hash_val, v.hash_persistent()))

        for v in self.const_vars:
            hash_val = hash_sha1((v[0].hash_persistent(), hash_sha1(v[1])))

        return hash_val

    def get_optimal_value_indices(self, result_var: bch.ParametrizedSweep) -> xr.DataArray:
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
        self, result_var: bch.ParametrizedSweep, keep_existing_consts: bool = True
    ) -> Tuple[bch.ParametrizedSweep, Any]:
        """Get a list of tuples of optimal variable names and value pairs, that can be fed in as constant values to subsequent parameter sweeps

        Args:
            result_var (bch.ParametrizedSweep): Optimal values of this result variable
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
        self,
        result_var: bch.ParametrizedSweep,
        input_vars: List[bch.ParametrizedSweep],
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

    def get_dataframe(self, reset_index=True) -> DataFrame:
        """Get the xarray results as a pandas dataframe

        Returns:
            pd.DataFrame: The xarray results array as a pandas dataframe
        """
        ds = self.ds.to_dataframe()
        if reset_index:
            return ds.reset_index()
        return ds

    def result_samples(self) -> int:
        """The number of samples in the results dataframe"""
        return len(self.get_dataframe().index)

    def get_best_trial_params(self, canonical=False):
        if len(self.studies) == 0:
            from bencher.optuna_conversions import bench_cfg_to_study

            self.studies = [bench_cfg_to_study(self, True)]
        out = self.studies[0].best_trials[0].params
        if canonical:
            return hmap_canonical_input(out)
        return out

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

    def get_pareto_front_params(self):
        return [p.params for p in self.studies[0].trials]

    def to_hv_dataset(self, reduce: ReduceType = ReduceType.AUTO) -> hv.Dataset:
        """Generate a holoviews dataset from the xarray dataset.

        Args:
            reduce (ReduceType, optional): Optionally perform reduce options on the dataset.  By default the returned dataset will calculate the mean and standard devation over the "repeat" dimension so that the dataset plays nicely with most of the holoviews plot types.  Reduce.Sqeeze is used if there is only 1 repeat and you want the "reduce" variable removed from the dataset. ReduceType.None returns an unaltered dataset. Defaults to ReduceType.AUTO.

        Returns:
            hv.Dataset: results in the form of a holoviews dataset
        """
        ds = convert_dataset_bool_dims_to_str(self.ds)

        if reduce == ReduceType.AUTO:
            reduce = ReduceType.REDUCE if self.repeats > 1 else ReduceType.SQUEEZE

        result_vars_str = [r.name for r in self.result_vars]
        kdims = [i.name for i in self.input_vars]
        kdims.append("repeat")  # repeat is always used
        hvds = hv.Dataset(ds, kdims=kdims, vdims=result_vars_str)
        if reduce == ReduceType.REDUCE:
            return hvds.reduce(["repeat"], np.mean, np.std)
        if reduce == ReduceType.SQUEEZE:
            return hv.Dataset(ds.squeeze("repeat", drop=True), vdims=result_vars_str)
        return hvds

    def to(self, hv_type: hv.Chart, reduce: ReduceType = ReduceType.AUTO, **kwargs) -> hv.Chart:
        return self.to_hv_dataset(reduce).to(hv_type, **kwargs)

    def to_curve(self, reduce: ReduceType = ReduceType.AUTO) -> hv.Curve:
        ds = self.to_hv_dataset(reduce)
        pt = ds.to(hv.Curve)
        if self.repeats > 1:
            pt *= ds.to(hv.Spread).opts(alpha=0.2)
        return pt

    def to_error_bar(self) -> hv.Bars:
        return self.to_hv_dataset(ReduceType.REDUCE).to(hv.ErrorBars)

    def to_points(self, reduce: ReduceType = ReduceType.AUTO) -> hv.Points:
        ds = self.to_hv_dataset(reduce)
        pt = ds.to(hv.Points)
        if reduce:
            pt *= ds.to(hv.ErrorBars)
        return pt

    def to_scatter(self):
        return self.to_hv_dataset(ReduceType.REDUCE).to(hv.Scatter)

    def to_scatter_jitter(self) -> hv.Scatter:
        ds = self.to_hv_dataset(ReduceType.NONE)
        pt = ds.to(hv.Scatter).opts(jitter=0.1).overlay("repeat").opts(show_legend=False)
        return pt

    def to_bar(self, reduce: ReduceType = ReduceType.AUTO) -> hv.Bars:
        ds = self.to_hv_dataset(reduce)
        pt = ds.to(hv.Bars)
        if reduce:
            pt *= ds.to(hv.ErrorBars)
        return pt

    def to_heatmap(self, reduce: ReduceType = ReduceType.AUTO, **kwargs) -> hv.HeatMap:
        z = self.result_vars[0]
        title = f"{z.name} vs ({self.input_vars[0].name}"

        for iv in self.input_vars[1:]:
            title += f" vs {iv.name}"
        title += ")"

        color_label = f"{z.name} [{z.units}]"

        return self.to(hv.HeatMap, reduce, **kwargs).opts(title=title, clabel=color_label)

    def to_heatmap_tap(self, reduce: ReduceType = ReduceType.AUTO, width=800, height=800, **kwargs):
        htmap = self.to_heatmap(reduce).opts(tools=["hover", "tap"], width=width, height=height)
        htmap_posxy = hv.streams.Tap(source=htmap, x=0, y=0)

        def tap_plot(x, y):
            kwargs[self.input_vars[0].name] = x
            kwargs[self.input_vars[1].name] = y
            return self.get_nearest_holomap(**kwargs).opts(width=width, height=height)

        tap_htmap = hv.DynamicMap(tap_plot, streams=[htmap_posxy])
        return htmap + tap_htmap

    def to_nd_layout(self, hmap_name: str) -> hv.NdLayout:
        print(self.hmap_kdims)
        return hv.NdLayout(self.get_hmap(hmap_name), kdims=self.hmap_kdims).opts(
            shared_axes=False, shared_datasource=False
        )

    def to_holomap(self, name: str = None) -> hv.HoloMap:
        return hv.HoloMap(self.to_nd_layout(name)).opts(shared_axes=False)

    def to_holomap_list(self, hmap_names: List[str] = None) -> hv.HoloMap:
        if hmap_names is None:
            hmap_names = [i.name for i in self.result_hmaps]
        col = pn.Column()
        for name in hmap_names:
            self.to_holomap(name)
        return col

    def get_nearest_holomap(self, name: str = None, **kwargs):
        canonical_inp = hmap_canonical_input(
            get_nearest_coords(self.ds, collapse_list=True, **kwargs)
        )
        return self.get_hmap(name)[canonical_inp].opts(framewise=True)

    def to_volume(self, **opts) -> pn.panel:
        from bencher.plt_cfg import BenchPlotter
        from bencher.plotting.plots.volume import VolumePlot
        from bencher.plotting.plot_collection import PlotInput

        # BenchPlotter.plot_result_variable()
        # return BenchPlotter.plot_results_row(self)
        return VolumePlot().volume_plotly(
            PlotInput(self, self.result_vars[0], BenchPlotter.generate_plt_cnt_cfg(self)), **opts
        )

    def to_dynamic_map(self, name: str = None) -> hv.DynamicMap:
        """use the values stored in the holomap dictionary to populate a dynamic map. Note that this is much faster than passing the holomap to a holomap object as the values are calculated on the fly"""

        def cb(**kwargs):
            return self.get_hmap(name)[hmap_canonical_input(kwargs)].opts(
                framewise=True, shared_axes=False
            )

        kdims = []
        for i in self.input_vars + [self.iv_repeat]:
            kdims.append(i.as_dim(compute_values=True, debug=self.debug))

        return hv.DynamicMap(cb, kdims=kdims)

    def to_grid(self, inputs=None):
        if inputs is None:
            inputs = self.inputs_as_str()
        if len(inputs) > 2:
            inputs = inputs[:2]
        return self.to_holomap().grid(inputs)

    def to_table(self):
        return self.to(hv.Table, ReduceType.SQUEEZE)

    def inputs_as_str(self) -> List[str]:
        return [i.name for i in self.input_vars]

    def describe_sweep(self) -> pn.pane.Markdown:
        """Produce a markdown summary of the sweep settings

        Returns:
            pn.pane.Markdown: _description_
        """
        return pn.pane.Markdown(
            describe_benchmark(self, self.summarise_constant_inputs), name=self.bench_name
        )

    def summarise_sweep(self, name=None, describe=True, results_suffix=True) -> pn.pane.Markdown:
        """Produce panel output summarising the title, description and sweep setting"""
        if name is None:
            name = self.title
        col = pn.Column(name=name)
        col.append(pn.pane.Markdown(f"# {self.title}"))
        if self.description is not None:
            col.append(pn.pane.Markdown(self.description, width=800))
        if describe:
            col.append(pn.pane.Markdown("## Data Collection Configuration:"))
            col.append(self.describe_sweep())
        if results_suffix:
            col.append(pn.pane.Markdown("## Results:"))
        return col

    def to_optuna(self) -> List[pn.pane.panel]:
        """Create an optuna summary from the benchmark results

        Returns:
            List[pn.pane.panel]: A list of optuna plot summarising the benchmark process
        """

        from bencher.optuna_conversions import collect_optuna_plots

        return collect_optuna_plots(self)

    def optuna_targets(self) -> List[str]:
        target_names = []
        for rv in self.result_vars:
            if rv.direction != OptDir.none:
                target_names.append(rv.name)
        return target_names


def describe_benchmark(bench_cfg: BenchCfg, summarise_constant_inputs) -> str:
    """Generate a string summary of the inputs and results from a BenchCfg

    Args:
        bench_cfg (BenchCfg): BenchCfg to generate a summary of

    Returns:
        str: summary of BenchCfg
    """
    benchmark_sampling_str = ["```text"]
    benchmark_sampling_str.append("")

    benchmark_sampling_str.append("Input Variables:")
    for iv in bench_cfg.input_vars:
        benchmark_sampling_str.extend(describe_variable(iv, bench_cfg.debug, True))

    if bench_cfg.const_vars and (bench_cfg.summarise_constant_inputs or summarise_constant_inputs):
        benchmark_sampling_str.append("\nConstants:")
        for cv in bench_cfg.const_vars:
            benchmark_sampling_str.extend(describe_variable(cv[0], False, False, cv[1]))

    benchmark_sampling_str.append("\nResult Variables:")
    for rv in bench_cfg.result_vars:
        benchmark_sampling_str.extend(describe_variable(rv, bench_cfg.debug, False))

    print_meta = True
    # if len(bench_cfg.meta_vars) == 1:
    #     mv = bench_cfg.meta_vars[0]
    #     if mv.name == "repeat" and mv.samples == 1:
    #         print_meta = False

    if print_meta:
        benchmark_sampling_str.append("\nMeta Variables:")
        benchmark_sampling_str.append(f"    run date: {bench_cfg.run_date}")
        if bench_cfg.run_tag is not None and len(bench_cfg.run_tag) > 0:
            benchmark_sampling_str.append(f"    run tag: {bench_cfg.run_tag}")
        if bench_cfg.level is not None:
            benchmark_sampling_str.append(f"    bench level: {bench_cfg.level}")
        benchmark_sampling_str.append(f"    use_cache: {bench_cfg.use_cache}")
        benchmark_sampling_str.append(f"    use_sample_cache: {bench_cfg.use_sample_cache}")
        benchmark_sampling_str.append(f"    only_hash_tag: {bench_cfg.only_hash_tag}")
        benchmark_sampling_str.append(f"    parallel: {bench_cfg.executor}")

        for mv in bench_cfg.meta_vars:
            benchmark_sampling_str.extend(describe_variable(mv, bench_cfg.debug, True))

    benchmark_sampling_str.append("```")

    benchmark_sampling_str = "\n".join(benchmark_sampling_str)
    return benchmark_sampling_str


def convert_dataset_bool_dims_to_str(dataset: xr.Dataset) -> xr.Dataset:
    """Given a dataarray that contains boolean coordinates, conver them to strings so that holoviews loads the data properly

    Args:
        dataarray (xr.DataArray): dataarray with boolean coordinates

    Returns:
        xr.DataArray: dataarray with boolean coordinates converted to strings
    """
    bool_coords = {}
    for c in dataset.coords:
        if dataset.coords[c].dtype == bool:
            bool_coords[c] = [str(vals) for vals in dataset.coords[c].values]

    if len(bool_coords) > 0:
        return dataset.assign_coords(bool_coords)
    return dataset


class DimsCfg:
    """A class to store data about the sampling and result dimensions"""

    def __init__(self, bench_cfg: BenchCfg) -> None:
        self.dims_name = [i.name for i in bench_cfg.all_vars]

        self.dim_ranges = []
        self.dim_ranges = [i.values(bench_cfg.debug) for i in bench_cfg.all_vars]
        self.dims_size = [len(p) for p in self.dim_ranges]
        self.dim_ranges_index = [list(range(i)) for i in self.dims_size]
        self.dim_ranges_str = [f"{s}\n" for s in self.dim_ranges]
        self.coords = dict(zip(self.dims_name, self.dim_ranges))

        logging.debug(f"dims_name: {self.dims_name}")
        logging.debug(f"dim_ranges {self.dim_ranges_str}")
        logging.debug(f"dim_ranges_index {self.dim_ranges_index}")
        logging.debug(f"coords: {self.coords}")
