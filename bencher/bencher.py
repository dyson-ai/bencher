import logging
from datetime import datetime
from itertools import product, combinations

from typing import Callable, List, Optional
from copy import deepcopy
import numpy as np
import param
import xarray as xr
from diskcache import Cache
from contextlib import suppress
from functools import partial
import panel as pn

from bencher.worker_job import WorkerJob

from bencher.bench_cfg import BenchCfg, BenchRunCfg, DimsCfg
from bencher.bench_plot_server import BenchPlotServer
from bencher.bench_report import BenchReport

from bencher.variables.inputs import IntSweep
from bencher.variables.time import TimeSnapshot, TimeEvent
from bencher.variables.results import (
    ResultVar,
    ResultVec,
    ResultHmap,
    ResultPath,
    ResultVideo,
    ResultImage,
    ResultString,
    ResultContainer,
    ResultReference,
    ResultDataSet,
)
from bencher.results.bench_result import BenchResult
from bencher.variables.parametrised_sweep import ParametrizedSweep
from bencher.job import Job, FutureCache, JobFuture, Executors
from bencher.utils import params_to_str

# Customize the formatter
formatter = logging.Formatter("%(levelname)s: %(message)s")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


for handler in logging.root.handlers:
    handler.setFormatter(formatter)


def set_xarray_multidim(data_array: xr.DataArray, index_tuple, value: float) -> xr.DataArray:
    # """This is terrible, I need to do this in a better way, but [] does not like *args syntax and the () version of the set function doesn't either"""
    match len(index_tuple):
        case 1:
            data_array[index_tuple[0]] = value
        case 2:
            data_array[index_tuple[0], index_tuple[1]] = value
        case 3:
            data_array[index_tuple[0], index_tuple[1], index_tuple[2]] = value
        case 4:
            data_array[index_tuple[0], index_tuple[1], index_tuple[2], index_tuple[3]] = value
        case 5:
            data_array[
                index_tuple[0], index_tuple[1], index_tuple[2], index_tuple[3], index_tuple[4]
            ] = value
        case 6:
            data_array[
                index_tuple[0],
                index_tuple[1],
                index_tuple[2],
                index_tuple[3],
                index_tuple[4],
                index_tuple[5],
            ] = value
        case 7:
            data_array[
                index_tuple[0],
                index_tuple[1],
                index_tuple[2],
                index_tuple[3],
                index_tuple[4],
                index_tuple[5],
                index_tuple[6],
            ] = value
        case 8:
            data_array[
                index_tuple[0],
                index_tuple[1],
                index_tuple[2],
                index_tuple[3],
                index_tuple[4],
                index_tuple[5],
                index_tuple[6],
                index_tuple[7],
            ] = value
        case 9:
            data_array[
                index_tuple[0],
                index_tuple[1],
                index_tuple[2],
                index_tuple[3],
                index_tuple[4],
                index_tuple[5],
                index_tuple[6],
                index_tuple[7],
                index_tuple[8],
            ] = value

    return data_array


def kwargs_to_input_cfg(worker_input_cfg: ParametrizedSweep, **kwargs) -> ParametrizedSweep:
    input_cfg = worker_input_cfg()
    input_cfg.param.update(kwargs)
    return input_cfg


def worker_cfg_wrapper(worker, worker_input_cfg: ParametrizedSweep, **kwargs) -> dict:
    input_cfg = kwargs_to_input_cfg(worker_input_cfg, **kwargs)
    return worker(input_cfg)


def worker_kwargs_wrapper(worker: Callable, bench_cfg: BenchCfg, **kwargs) -> dict:
    function_input_deep = deepcopy(kwargs)
    if not bench_cfg.pass_repeat:
        function_input_deep.pop("repeat")
    if "over_time" in function_input_deep:
        function_input_deep.pop("over_time")
    if "time_event" in function_input_deep:
        function_input_deep.pop("time_event")
    return worker(**function_input_deep)


class Bench(BenchPlotServer):
    def __init__(
        self,
        bench_name: str = None,
        worker: Callable | ParametrizedSweep = None,
        worker_input_cfg: ParametrizedSweep = None,
        run_cfg=None,
        report=None,
    ) -> None:
        """Create a new Bench object from a function and a class defining the inputs to the function

        Args:
            bench_name (str): The name of the benchmark and output folder for the figures
            worker (Callable | ParametrizedSweep): A function that accepts a class of type (worker_input_config)
            worker_input_config (ParametrizedSweep): A class defining the parameters of the function.
        """
        assert isinstance(bench_name, str)
        self.bench_name = bench_name
        self.worker = None
        self.worker_class_instance = None
        self.worker_input_cfg = None
        self.worker_class_instance = None
        self.set_worker(worker, worker_input_cfg)
        self.run_cfg = run_cfg
        if report is None:
            self.report = BenchReport(self.bench_name)
        else:
            self.report = report
            if self.report.bench_name is None:
                self.report.bench_name = self.bench_name
        self.results = []

        self.bench_cfg_hashes = []  # a list of hashes that point to benchmark results
        self.last_run_cfg = None  # cached run_cfg used to pass to the plotting function
        self.sample_cache = None  # store the results of each benchmark function call in a cache
        self.ds_dynamic = {}  # A dictionary to store unstructured vector datasets

        self.cache_size = int(100e9)  # default to 100gb

        # self.bench_cfg = BenchCfg()

        # Maybe put this in SweepCfg
        self.input_vars = None
        self.result_vars = None
        self.const_vars = None
        self.plot_callbacks = []
        self.plot = True

    def add_plot_callback(self, callback: Callable[[BenchResult], pn.panel], **kwargs) -> None:
        """Add a plotting callback that will be called on any result produced when calling a sweep funciton.  You can pass additional arguments to the plotting function with kwargs.  e.g.  add_plot_callback(bch.BenchResult.to_video_grid,)

        Args:
            callback (Callable[[BenchResult], pn.panel]): _description_
        """
        self.plot_callbacks.append(partial(callback, **kwargs))

    def set_worker(self, worker: Callable, worker_input_cfg: ParametrizedSweep = None) -> None:
        """Set the benchmark worker function and optionally the type the worker expects

        Args:
            worker (Callable): The benchmark worker function
            worker_input_cfg (ParametrizedSweep, optional): The input type the worker expects. Defaults to None.
        """

        if isinstance(worker, ParametrizedSweep):
            self.worker_class_instance = worker
            # self.worker_class_type = type(worker)
            self.worker = self.worker_class_instance.__call__
            logging.info("setting worker from bench class.__call__")
        else:
            if isinstance(worker, type):
                raise RuntimeError("This should be a class instance, not a class")
            if worker_input_cfg is None:
                self.worker = worker
            else:
                self.worker = partial(worker_cfg_wrapper, worker, worker_input_cfg)
            logging.info(f"setting worker {worker}")
        self.worker_input_cfg = worker_input_cfg

    def sweep_sequential(
        self,
        title="",
        input_vars: List[ParametrizedSweep] = None,
        result_vars: List[ParametrizedSweep] = None,
        const_vars: List[ParametrizedSweep] = None,
        optimise_var: ParametrizedSweep = None,
        run_cfg: BenchRunCfg = None,
        group_size: int = 1,
        iterations: int = 1,
        relationship_cb=None,
        plot_callbacks: List | bool = None,
    ) -> List[BenchResult]:
        if relationship_cb is None:
            relationship_cb = combinations
        if input_vars is None:
            input_vars = self.worker_class_instance.get_inputs_only()
        results = []
        for it in range(iterations):
            for input_group in relationship_cb(input_vars, group_size):
                title_gen = title + "Sweeping " + " vs ".join(params_to_str(input_group))
                if iterations > 1:
                    title_gen += f" iteration:{it}"
                res = self.plot_sweep(
                    title=title_gen,
                    input_vars=list(input_group),
                    result_vars=result_vars,
                    const_vars=const_vars,
                    run_cfg=run_cfg,
                    plot_callbacks=plot_callbacks,
                )

                if optimise_var is not None:
                    const_vars = res.get_optimal_inputs(optimise_var, True)
                results.append(res)
        return results

    def plot_sweep(
        self,
        title: str = None,
        input_vars: List[ParametrizedSweep] = None,
        result_vars: List[ParametrizedSweep] = None,
        const_vars: List[ParametrizedSweep] = None,
        time_src: datetime = None,
        description: str = None,
        post_description: str = None,
        pass_repeat: bool = False,
        tag: str = "",
        run_cfg: BenchRunCfg = None,
        plot_callbacks: List | bool = None,
    ) -> BenchResult:
        """The all in 1 function benchmarker and results plotter.

        Args:
            input_vars (List[ParametrizedSweep], optional): _description_. Defaults to None.
            result_vars (List[ParametrizedSweep], optional): _description_. Defaults to None.
            const_vars (List[ParametrizedSweep], optional): A list of variables to keep constant with a specified value. Defaults to None.
            title (str, optional): The title of the benchmark. Defaults to None.
            description (str, optional): A description of the benchmark. Defaults to None.
            post_description (str, optional): A description that comes after the benchmark plots. Defaults to None.
            time_src (datetime, optional): Set a time that the result was generated. Defaults to datetime.now().
            pass_repeat (bool,optional) By default do not pass the kwarg 'repeat' to the benchmark function.  Set to true if
            you want the benchmark function to be passed the repeat number
            tag (str,optional): Use tags to group different benchmarks together.
            run_cfg: (BenchRunCfg, optional): A config for storing how the benchmarks and run
            plot_callbacks: (List | bool) A list of plot callbacks to call on the results. Pass false or an empty list to turn off plotting
        Raises:
            ValueError: If a result variable is not set

        Returns:
            BenchResult: A class with all the data used to generate the results and the results
        """

        input_vars_in = deepcopy(input_vars)
        result_vars_in = deepcopy(result_vars)
        const_vars_in = deepcopy(const_vars)

        if self.worker_class_instance is not None:
            if input_vars_in is None:
                logging.info(
                    "No input variables passed, using all param variables in bench class as inputs"
                )
                if self.input_vars is None:
                    input_vars_in = self.worker_class_instance.get_inputs_only()
                else:
                    input_vars_in = deepcopy(self.input_vars)
                for i in input_vars_in:
                    logging.info(f"input var: {i.name}")
            if result_vars_in is None:
                logging.info(
                    "No results variables passed, using all result variables in bench class:"
                )
                if self.result_vars is None:
                    result_vars_in = self.worker_class_instance.get_results_only()
                else:
                    result_vars_in = deepcopy(self.result_vars)

            if const_vars_in is None:
                if self.const_vars is None:
                    const_vars_in = self.worker_class_instance.get_input_defaults()
                else:
                    const_vars_in = deepcopy(self.const_vars)
        else:
            if input_vars_in is None:
                input_vars_in = []
            if result_vars_in is None:
                result_vars_in = []
            if const_vars_in is None:
                const_vars_in = []

        if run_cfg is None:
            if self.run_cfg is None:
                run_cfg = BenchRunCfg()
                logging.info("Generate default run cfg")
            else:
                run_cfg = deepcopy(self.run_cfg)
                logging.info("Copy run cfg from bench class")

        if run_cfg.only_plot:
            run_cfg.use_cache = True

        self.last_run_cfg = run_cfg

        if isinstance(input_vars_in, dict):
            input_lists = []
            for k, v in input_vars_in.items():
                param_var = self.convert_vars_to_params(k, "input", run_cfg)
                if isinstance(v, list):
                    assert len(v) > 0
                    param_var = param_var.with_sample_values(v)

                else:
                    raise RuntimeError("Unsupported type")
                input_lists.append(param_var)

            input_vars_in = input_lists
        else:
            for i in range(len(input_vars_in)):
                input_vars_in[i] = self.convert_vars_to_params(input_vars_in[i], "input", run_cfg)
        for i in range(len(result_vars_in)):
            result_vars_in[i] = self.convert_vars_to_params(result_vars_in[i], "result", run_cfg)

        for r in result_vars_in:
            logging.info(f"result var: {r.name}")

        if isinstance(const_vars_in, dict):
            const_vars_in = list(const_vars_in.items())

        for i in range(len(const_vars_in)):
            # consts come as tuple pairs
            cv_list = list(const_vars_in[i])
            cv_list[0] = self.convert_vars_to_params(cv_list[0], "const", run_cfg)
            const_vars_in[i] = cv_list

        if title is None:
            if len(input_vars_in) > 0:
                title = "Sweeping " + " vs ".join([i.name for i in input_vars_in])
            elif len(const_vars_in) > 0:
                title = "Constant Value"
                if len(const_vars_in) > 1:
                    title += "s"
                title += ": " + ", ".join([f"{c[0].name}={c[1]}" for c in const_vars_in])
            else:
                raise RuntimeError("you must pass a title, or define inputs or consts")

        if run_cfg.level > 0:
            inputs = []
            print(input_vars_in)
            if len(input_vars_in) > 0:
                for i in input_vars_in:
                    inputs.append(i.with_level(run_cfg.level))
                input_vars_in = inputs

        # if any of the inputs have been include as constants, remove those variables from the list of constants
        with suppress(ValueError, AttributeError):
            for i in input_vars_in:
                for c in const_vars_in:
                    # print(i.hash_persistent())
                    if i.name == c[0].name:
                        const_vars_in.remove(c)
                        logging.info(f"removing {i.name} from constants")

        result_hmaps = []
        result_vars_only = []
        for i in result_vars_in:
            if isinstance(i, ResultHmap):
                result_hmaps.append(i)
            else:
                result_vars_only.append(i)

        if post_description is None:
            post_description = (
                "## Results Description\nPlease set post_description to explain these results"
            )

        if plot_callbacks is None:
            if self.plot_callbacks is not None and len(self.plot_callbacks) == 0:
                plot_callbacks = [BenchResult.to_auto_plots]
            else:
                plot_callbacks = self.plot_callbacks
        elif isinstance(plot_callbacks, bool):
            plot_callbacks = [BenchResult.to_auto_plots] if plot_callbacks else []

        bench_cfg = BenchCfg(
            input_vars=input_vars_in,
            result_vars=result_vars_only,
            result_hmaps=result_hmaps,
            const_vars=const_vars_in,
            bench_name=self.bench_name,
            description=description,
            post_description=post_description,
            title=title,
            pass_repeat=pass_repeat,
            tag=run_cfg.run_tag + tag,
            plot_callbacks=plot_callbacks,
        )
        return self.run_sweep(bench_cfg, run_cfg, time_src)

    def run_sweep(
        self, bench_cfg: BenchCfg, run_cfg: BenchRunCfg, time_src: datetime
    ) -> BenchResult:
        print("tag", bench_cfg.tag)

        bench_cfg.param.update(run_cfg.param.values())
        bench_cfg_hash = bench_cfg.hash_persistent(True)
        bench_cfg.hash_value = bench_cfg_hash

        # does not include repeats in hash as sample_hash already includes repeat as part of the per sample hash
        bench_cfg_sample_hash = bench_cfg.hash_persistent(False)

        if self.sample_cache is None:
            self.sample_cache = self.init_sample_cache(run_cfg)
        if bench_cfg.clear_sample_cache:
            self.clear_tag_from_sample_cache(bench_cfg.tag, run_cfg)

        calculate_results = True
        with Cache("cachedir/benchmark_inputs", size_limit=self.cache_size) as c:
            if run_cfg.clear_cache:
                c.delete(bench_cfg_hash)
                logging.info("cleared cache")
            elif run_cfg.use_cache:
                logging.info(
                    f"checking for previously calculated results with key: {bench_cfg_hash}"
                )
                if bench_cfg_hash in c:
                    logging.info(f"loading cached results from key: {bench_cfg_hash}")
                    bench_res = c[bench_cfg_hash]
                    # if not over_time:  # if over time we always want to calculate results
                    calculate_results = False
                else:
                    logging.info("did not detect results in cache")
                    if run_cfg.only_plot:
                        raise FileNotFoundError("Was not able to load the results to plot!")

        if calculate_results:
            if run_cfg.time_event is not None:
                time_src = run_cfg.time_event
            bench_res = self.calculate_benchmark_results(
                bench_cfg, time_src, bench_cfg_sample_hash, run_cfg
            )

            # use the hash of the inputs to look up historical values in the cache
            if run_cfg.over_time:
                bench_res.ds = self.load_history_cache(
                    bench_res.ds, bench_cfg_hash, run_cfg.clear_history
                )

            self.report_results(bench_res, run_cfg.print_xarray, run_cfg.print_pandas)
            self.cache_results(bench_res, bench_cfg_hash)

        logging.info(self.sample_cache.stats())
        self.sample_cache.close()

        bench_res.post_setup()

        if bench_cfg.auto_plot:
            self.report.append_result(bench_res)

        self.results.append(bench_res)
        return bench_res

    def convert_vars_to_params(
        self,
        variable: param.Parameter | str | dict | tuple,
        var_type: str,
        run_cfg: Optional[BenchRunCfg],
    ) -> param.Parameter:
        """check that a variable is a subclass of param

        Args:
            variable (param.Parameter): the varible to check
            var_type (str): a string representation of the variable type for better error messages

        Raises:
            TypeError: the input variable type is not a param.
        """
        if isinstance(variable, str):
            variable = self.worker_class_instance.param.objects(instance=False)[variable]
        if isinstance(variable, dict):
            param_var = self.worker_class_instance.param.objects(instance=False)[variable["name"]]
            if variable.get("values"):
                param_var = param_var.with_sample_values(variable["values"])

            if variable.get("samples"):
                param_var = param_var.with_samples(variable["samples"])
            if variable.get("max_level"):
                if run_cfg is not None:
                    param_var = param_var.with_level(run_cfg.level, variable["max_level"])
            variable = param_var
        if not isinstance(variable, param.Parameter):
            raise TypeError(
                f"You need to use {var_type}_vars =[{self.worker_input_cfg}.param.your_variable], instead of {var_type}_vars =[{self.worker_input_cfg}.your_variable]"
            )
        return variable

    def cache_results(self, bench_res: BenchResult, bench_cfg_hash: int) -> None:
        with Cache("cachedir/benchmark_inputs", size_limit=self.cache_size) as c:
            logging.info(f"saving results with key: {bench_cfg_hash}")
            self.bench_cfg_hashes.append(bench_cfg_hash)
            # object index may not be pickleable so remove before caching
            obj_index_tmp = bench_res.object_index
            bench_res.object_index = []

            c[bench_cfg_hash] = bench_res

            # restore object index
            bench_res.object_index = obj_index_tmp

            logging.info(f"saving benchmark: {self.bench_name}")
            c[self.bench_name] = self.bench_cfg_hashes

    # def show(self, run_cfg: BenchRunCfg = None, pane=None) -> None:
    #     """Launches a webserver with plots of the benchmark results, blocking

    #     Args:
    #         run_cfg (BenchRunCfg, optional): Options for the webserve such as the port. Defaults to None.

    #     """
    #     if run_cfg is None:
    #         if self.last_run_cfg is not None:
    #             run_cfg = self.last_run_cfg
    #         else:
    #             run_cfg = BenchRunCfg()

    #     return BenchPlotServer().plot_server(self.bench_name, run_cfg, pane)

    def load_history_cache(
        self, dataset: xr.Dataset, bench_cfg_hash: int, clear_history: bool
    ) -> xr.Dataset:
        """Load historical data from a cache if over_time=true

        Args:
            ds (xr.Dataset): Freshly calcuated data
            bench_cfg_hash (int): Hash of the input variables used to generate the data
            clear_history (bool): Optionally clear the history

        Returns:
            xr.Dataset: historical data as an xr dataset
        """
        with Cache("cachedir/history", size_limit=self.cache_size) as c:
            if clear_history:
                logging.info("clearing history")
            else:
                logging.info(f"checking historical key: {bench_cfg_hash}")
                if bench_cfg_hash in c:
                    logging.info("loading historical data from cache")
                    ds_old = c[bench_cfg_hash]
                    dataset = xr.concat([ds_old, dataset], "over_time")
                else:
                    logging.info("did not detect any historical data")

            logging.info("saving data to history cache")
            c[bench_cfg_hash] = dataset
        return dataset

    def setup_dataset(
        self, bench_cfg: BenchCfg, time_src: datetime | str
    ) -> tuple[BenchResult, List, List]:
        """A function for generating an n-d xarray from a set of input variables in the BenchCfg

        Args:
            bench_cfg (BenchCfg): description of the benchmark parameters
            time_src (datetime | str): a representation of the sample time

        Returns:
            tuple[BenchResult, List, List]: bench_result, function intputs, dimension names
        """

        if time_src is None:
            time_src = datetime.now()
        bench_cfg.meta_vars = self.define_extra_vars(bench_cfg, bench_cfg.repeats, time_src)

        bench_cfg.all_vars = bench_cfg.input_vars + bench_cfg.meta_vars
        # bench_cfg.all_vars = bench_cfg.iv_time + bench_cfg.input_vars +[ bench_cfg.iv_repeat]
        # bench_cfg.all_vars = [ bench_cfg.iv_repeat] +bench_cfg.input_vars + bench_cfg.iv_time

        for i in bench_cfg.all_vars:
            logging.info(i.sampling_str())

        dims_cfg = DimsCfg(bench_cfg)
        function_inputs = list(
            zip(product(*dims_cfg.dim_ranges_index), product(*dims_cfg.dim_ranges))
        )
        # xarray stores K N-dimensional arrays of data.  Each array is named and in this case we have a nd array for each result variable
        data_vars = {}
        dataset_list = []

        for rv in bench_cfg.result_vars:
            if isinstance(rv, ResultVar):
                result_data = np.full(dims_cfg.dims_size, np.nan, dtype=float)
                data_vars[rv.name] = (dims_cfg.dims_name, result_data)
            if isinstance(rv, (ResultReference, ResultDataSet)):
                result_data = np.full(dims_cfg.dims_size, -1, dtype=int)
                data_vars[rv.name] = (dims_cfg.dims_name, result_data)
            if isinstance(
                rv, (ResultPath, ResultVideo, ResultImage, ResultString, ResultContainer)
            ):
                result_data = np.full(dims_cfg.dims_size, "NAN", dtype=object)
                data_vars[rv.name] = (dims_cfg.dims_name, result_data)

            elif type(rv) is ResultVec:
                for i in range(rv.size):
                    result_data = np.full(dims_cfg.dims_size, np.nan)
                    data_vars[rv.index_name(i)] = (dims_cfg.dims_name, result_data)

        bench_res = BenchResult(bench_cfg)
        bench_res.ds = xr.Dataset(data_vars=data_vars, coords=dims_cfg.coords)
        bench_res.ds_dynamic = self.ds_dynamic
        bench_res.dataset_list = dataset_list
        bench_res.setup_object_index()

        return bench_res, function_inputs, dims_cfg.dims_name

    def define_const_inputs(self, const_vars) -> dict:
        constant_inputs = None
        if const_vars is not None:
            const_vars, constant_values = [
                [i for i, j in const_vars],
                [j for i, j in const_vars],
            ]

            constant_names = [i.name for i in const_vars]
            constant_inputs = dict(zip(constant_names, constant_values))
        return constant_inputs

    def define_extra_vars(self, bench_cfg: BenchCfg, repeats: int, time_src) -> list[IntSweep]:
        """Define extra meta vars that are stored in the n-d array but are not passed to the benchmarking function, such as number of repeats and the time the function was called.

        Args:
            bench_cfg (BenchCfg): description of the benchmark parameters
            repeats (int): the number of times to sample the function
            time_src (datetime): a representation of the sample time

        Returns:
            _type_: _description_
        """
        bench_cfg.iv_repeat = IntSweep(
            default=repeats,
            bounds=[1, repeats],
            samples=repeats,
            units="repeats",
            doc="The number of times a sample was measured",
        )
        bench_cfg.iv_repeat.name = "repeat"
        extra_vars = [bench_cfg.iv_repeat]

        if bench_cfg.over_time:
            if isinstance(time_src, str):
                iv_over_time = TimeEvent(time_src)
            else:
                iv_over_time = TimeSnapshot(time_src)
            iv_over_time.name = "over_time"
            extra_vars.append(iv_over_time)
            bench_cfg.iv_time = [iv_over_time]
        return extra_vars

    def calculate_benchmark_results(
        self, bench_cfg, time_src: datetime | str, bench_cfg_sample_hash, bench_run_cfg
    ) -> BenchResult:
        """A function for generating an n-d xarray from a set of input variables in the BenchCfg

        Args:
            bench_cfg (BenchCfg): description of the benchmark parameters
            time_src (datetime): a representation of the sample time

        Returns:
            bench_cfg (BenchCfg): description of the benchmark parameters
        """
        bench_res, func_inputs, dims_name = self.setup_dataset(bench_cfg, time_src)
        bench_res.bench_cfg.hmap_kdims = sorted(dims_name)
        constant_inputs = self.define_const_inputs(bench_res.bench_cfg.const_vars)
        callcount = 1

        results_list = []
        jobs = []

        for idx_tuple, function_input_vars in func_inputs:
            job = WorkerJob(
                function_input_vars,
                idx_tuple,
                dims_name,
                constant_inputs,
                bench_cfg_sample_hash,
                bench_res.bench_cfg.tag,
            )
            job.setup_hashes()
            jobs.append(job)

            jid = f"{bench_res.bench_cfg.title}:call {callcount}/{len(func_inputs)}"
            worker = partial(worker_kwargs_wrapper, self.worker, bench_res.bench_cfg)
            cache_job = Job(
                job_id=jid,
                function=worker,
                job_args=job.function_input,
                job_key=job.function_input_signature_pure,
                tag=job.tag,
            )
            result = self.sample_cache.submit(cache_job)
            results_list.append(result)
            callcount += 1

            if bench_run_cfg.executor == Executors.SERIAL:
                self.store_results(result, bench_res, job, bench_run_cfg)

        if bench_run_cfg.executor != Executors.SERIAL:
            for job, res in zip(jobs, results_list):
                self.store_results(res, bench_res, job, bench_run_cfg)

        for inp in bench_res.bench_cfg.all_vars:
            self.add_metadata_to_dataset(bench_res, inp)

        return bench_res

    def store_results(
        self,
        job_result: JobFuture,
        bench_res: BenchResult,
        worker_job: WorkerJob,
        bench_run_cfg: BenchRunCfg,
    ) -> None:
        result = job_result.result()
        if result is not None:
            logging.info(f"{job_result.job.job_id}:")
            if bench_res.bench_cfg.print_bench_inputs:
                for k, v in worker_job.function_input.items():
                    logging.info(f"\t {k}:{v}")

            result_dict = result if isinstance(result, dict) else result.param.values()

            for rv in bench_res.bench_cfg.result_vars:
                result_value = result_dict[rv.name]
                if bench_run_cfg.print_bench_results:
                    logging.info(f"{rv.name}: {result_value}")

                if isinstance(
                    rv,
                    (
                        ResultVar,
                        ResultVideo,
                        ResultImage,
                        ResultString,
                        ResultContainer,
                        ResultPath,
                    ),
                ):
                    set_xarray_multidim(bench_res.ds[rv.name], worker_job.index_tuple, result_value)
                elif isinstance(rv, ResultDataSet):
                    bench_res.dataset_list.append(result_value)
                    set_xarray_multidim(
                        bench_res.ds[rv.name],
                        worker_job.index_tuple,
                        len(bench_res.dataset_list) - 1,
                    )
                elif isinstance(rv, ResultReference):
                    bench_res.object_index.append(result_value)
                    set_xarray_multidim(
                        bench_res.ds[rv.name],
                        worker_job.index_tuple,
                        len(bench_res.object_index) - 1,
                    )

                elif isinstance(rv, ResultVec):
                    if isinstance(result_value, (list, np.ndarray)):
                        if len(result_value) == rv.size:
                            for i in range(rv.size):
                                set_xarray_multidim(
                                    bench_res.ds[rv.index_name(i)],
                                    worker_job.index_tuple,
                                    result_value[i],
                                )

                else:
                    raise RuntimeError("Unsupported result type")
            for rv in bench_res.result_hmaps:
                bench_res.hmaps[rv.name][worker_job.canonical_input] = result_dict[rv.name]

            # bench_cfg.hmap = bench_cfg.hmaps[bench_cfg.result_hmaps[0].name]

    def init_sample_cache(self, run_cfg: BenchRunCfg):
        return FutureCache(
            overwrite=run_cfg.overwrite_sample_cache,
            executor=run_cfg.executor,
            cache_name="sample_cache",
            tag_index=True,
            size_limit=self.cache_size,
            use_cache=run_cfg.use_sample_cache,
        )

    def clear_tag_from_sample_cache(self, tag: str, run_cfg):
        """Clear all samples from the cache that match a tag
        Args:
            tag(str): clear samples with this tag
        """
        if self.sample_cache is None:
            self.sample_cache = self.init_sample_cache(run_cfg)
        self.sample_cache.clear_tag(tag)

    def add_metadata_to_dataset(self, bench_res: BenchResult, input_var: ParametrizedSweep) -> None:
        """Adds variable metadata to the xrarry so that it can be used to automatically plot the dimension units etc.

        Args:
            bench_cfg (BenchCfg):
            input_var (ParametrizedSweep): The varible to extract metadata from
        """

        for rv in bench_res.bench_cfg.result_vars:
            if type(rv) is ResultVar:
                bench_res.ds[rv.name].attrs["units"] = rv.units
                bench_res.ds[rv.name].attrs["long_name"] = rv.name
            elif type(rv) is ResultVec:
                for i in range(rv.size):
                    bench_res.ds[rv.index_name(i)].attrs["units"] = rv.units
                    bench_res.ds[rv.index_name(i)].attrs["long_name"] = rv.name
            else:
                pass  # todo

        dsvar = bench_res.ds[input_var.name]
        dsvar.attrs["long_name"] = input_var.name
        if input_var.units is not None:
            dsvar.attrs["units"] = input_var.units
        if input_var.__doc__ is not None:
            dsvar.attrs["description"] = input_var.__doc__

    def report_results(self, bench_cfg: BenchCfg, print_xarray: bool, print_pandas: bool):
        """Optionally display the caculated benchmark data as either as pandas, xarray or plot

        Args:
            bench_cfg (BenchCfg):
            print_xarray (bool):
            print_pandas (bool):
        """
        if print_xarray:
            logging.info(bench_cfg.ds)
        if print_pandas:
            logging.info(bench_cfg.ds.to_dataframe())

    def clear_call_counts(self) -> None:
        """Clear the worker and cache call counts, to help debug and assert caching is happening properly"""
        self.sample_cache.clear_call_counts()

    def get_result(self, index: int = -1) -> BenchResult:
        return self.results[index]

    def publish(self, remote_callback: Callable) -> str:
        branch_name = f"{self.bench_name}_{self.run_cfg.run_tag}"
        return self.report.publish(remote_callback, branch_name=branch_name)
