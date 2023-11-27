import logging
from datetime import datetime
from itertools import product
from typing import Callable, List
from copy import deepcopy
import numpy as np
import param
import xarray as xr
from diskcache import Cache
from contextlib import suppress
from optuna import Study
from functools import partial

from bencher.worker_job import WorkerJob

from bencher.bench_cfg import BenchCfg, BenchRunCfg, DimsCfg
from bencher.bench_plot_server import BenchPlotServer
from bencher.bench_report import BenchReport

from bencher.variables.inputs import IntSweep
from bencher.variables.time import TimeSnapshot, TimeEvent
from bencher.variables.results import ResultVar, ResultVec, ResultHmap

from bencher.variables.parametrised_sweep import ParametrizedSweep

from bencher.plotting.plot_collection import PlotCollection
from bencher.plotting.plot_library import PlotLibrary  # noqa pylint: disable=unused-import

from bencher.optuna_conversions import to_optuna, summarise_study

from bencher.job import Job, FutureCache, JobFuture, Executors

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
    for k, v in kwargs.items():
        input_cfg.param.set_param(k, v)
    return input_cfg


def worker_cfg_wrapper(worker, worker_input_cfg: ParametrizedSweep, **kwargs) -> dict:
    input_cfg = kwargs_to_input_cfg(worker_input_cfg, **kwargs)
    return worker(input_cfg)


def worker_kwargs_wrapper(worker, bench_cfg, **kwargs) -> dict:
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
        plot_lib: PlotCollection = None,
        remove_plots: list = None,
        run_cfg=None,
        report=None,
    ) -> None:
        """Create a new Bench object from a function and a class defining the inputs to the function

        Args:
            bench_name (str): The name of the benchmark and output folder for the figures
            worker (Callable | ParametrizedSweep): A function that accepts a class of type (worker_input_config)
            worker_input_config (ParametrizedSweep): A class defining the parameters of the function.
            plot_lib: (PlotCollection):  A dictionary of plot names:method pairs that are selected for plotting based on the type of data they can plot.
        """
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

        self.bench_cfg_hashes = []  # a list of hashes that point to benchmark results
        self.last_run_cfg = None  # cached run_cfg used to pass to the plotting function
        self.sample_cache = None  # store the results of each benchmark function call in a cache
        self.ds_dynamic = {}  # A dictionary to store unstructured vector datasets
        self.plot_lib = PlotLibrary.default() if plot_lib is None else plot_lib
        self.cache_size = int(100e9)  # default to 100gb
        if remove_plots is not None:
            for i in remove_plots:
                self.plot_lib.remove(i)

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

    def to_optuna(
        self,
        input_vars: List[ParametrizedSweep],
        result_vars: List[ParametrizedSweep],
        n_trials: int = 100,
    ) -> Study:
        bench_cfg = BenchCfg(
            input_vars=input_vars,
            result_vars=result_vars,
            bench_name=self.bench_name,
        )
        return self.to_optuna_from_sweep(bench_cfg, n_trials)

    def to_optuna_from_sweep(
        self,
        bench_cfg: BenchCfg,
        n_trials: int = 100,
    ) -> Study:
        optu = to_optuna(self.worker, bench_cfg, n_trials=n_trials)
        self.report.append(summarise_study(optu))
        return optu

    def plot_sweep(
        self,
        title: str,
        input_vars: List[ParametrizedSweep] = None,
        result_vars: List[ParametrizedSweep] = None,
        const_vars: List[ParametrizedSweep] = None,
        time_src: datetime = None,
        description: str = None,
        post_description: str = None,
        pass_repeat: bool = False,
        tag: str = "",
        run_cfg: BenchRunCfg = None,
        plot_lib=None,
    ) -> BenchCfg:
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
            run_cfg: (BenchRunCfg, optional): A config for storing how the benchmarks and run and plotted
            plot_lib: (PlotCollection):  A dictionary of plot names:method pairs that are selected for plotting based on the type of data they can plot.

        Raises:
            ValueError: If a result variable is not set

        Returns:
            BenchCfg: A class with all the data used to generate the results and the results
        """

        if self.worker_class_instance is not None:
            if input_vars is None:
                logging.info(
                    "No input variables passed, using all param variables in bench class as inputs"
                )
                input_vars = self.worker_class_instance.get_inputs_only()
                for i in input_vars:
                    logging.info(i.name)
            if result_vars is None:
                logging.info(
                    "No results variables passed, using all result variables in bench class:"
                )
                result_vars = self.worker_class_instance.get_results_only()
                for r in result_vars:
                    logging.info(f"result var: {r.name}")
            if const_vars is None:
                const_vars = self.worker_class_instance.get_input_defaults()
        else:
            if input_vars is None:
                input_vars = []
            if result_vars is None:
                result_vars = []
            if const_vars is None:
                const_vars = []
            else:
                const_vars = deepcopy(const_vars)

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

        if run_cfg.level > 0:
            inputs = []
            for i in input_vars:
                inputs.append(i.with_level(run_cfg.level))
            input_vars = inputs

        # if any of the inputs have been include as constants, remove those variables from the list of constants
        with suppress(ValueError, AttributeError):
            for i in input_vars:
                for c in const_vars:
                    # print(i.hash_persistent())
                    if i.name == c[0].name:
                        const_vars.remove(c)
                        logging.info(f"removing {i.name} from constants")

        for i in input_vars:
            self.check_var_is_a_param(i, "input")
        for i in result_vars:
            self.check_var_is_a_param(i, "result")
        for i in const_vars:
            # consts come as tuple pairs
            self.check_var_is_a_param(i[0], "const")

        result_hmaps = []
        result_vars_only = []
        for i in result_vars:
            if isinstance(i, ResultHmap):
                result_hmaps.append(i)
            else:
                result_vars_only.append(i)

        if post_description is None:
            post_description = (
                "## Results Description\nPlease set post_description to explain these results"
            )

        bench_cfg = BenchCfg(
            input_vars=input_vars,
            result_vars=result_vars_only,
            result_hmaps=result_hmaps,
            const_vars=const_vars,
            bench_name=self.bench_name,
            description=description,
            post_description=post_description,
            title=title,
            pass_repeat=pass_repeat,
            tag=run_cfg.run_tag + tag,
        )
        print("tag", bench_cfg.tag)

        bench_cfg.param.update(run_cfg.param.values())
        bench_cfg.plot_lib = plot_lib if plot_lib is not None else self.plot_lib

        print("plot_lib", bench_cfg.plot_lib)

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
                    bench_cfg = c[bench_cfg_hash]
                    # if not over_time:  # if over time we always want to calculate results
                    calculate_results = False
                else:
                    logging.info("did not detect results in cache")
                    if run_cfg.only_plot:
                        raise FileNotFoundError("Was not able to load the results to plot!")

        if calculate_results:
            if run_cfg.time_event is not None:
                time_src = run_cfg.time_event
            bench_cfg = self.calculate_benchmark_results(
                bench_cfg, time_src, bench_cfg_sample_hash, run_cfg
            )

            # use the hash of the inputs to look up historical values in the cache
            if run_cfg.over_time:
                bench_cfg.ds = self.load_history_cache(
                    bench_cfg.ds, bench_cfg_hash, run_cfg.clear_history
                )

            self.report_results(bench_cfg, run_cfg.print_xarray, run_cfg.print_pandas)
            self.cache_results(bench_cfg, bench_cfg_hash)

        logging.info(self.sample_cache.stats())
        self.sample_cache.close()

        if bench_cfg.auto_plot:
            self.report.append_result(bench_cfg)

        return bench_cfg

    def check_var_is_a_param(self, variable: param.Parameter, var_type: str):
        """check that a variable is a subclass of param

        Args:
            variable (param.Parameter): the varible to check
            var_type (str): a string representation of the variable type for better error messages

        Raises:
            TypeError: the input variable type is not a param.
        """
        if not isinstance(variable, param.Parameter):
            raise TypeError(
                f"You need to use {var_type}_vars =[{self.worker_input_cfg}.param.your_variable], instead of {var_type}_vars =[{self.worker_input_cfg}.your_variable]"
            )

    def cache_results(self, bench_cfg: BenchCfg, bench_cfg_hash: int) -> None:
        with Cache("cachedir/benchmark_inputs", size_limit=self.cache_size) as c:
            logging.info(f"saving results with key: {bench_cfg_hash}")
            self.bench_cfg_hashes.append(bench_cfg_hash)
            c[bench_cfg_hash] = bench_cfg
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
        self, ds: xr.Dataset, bench_cfg_hash: int, clear_history: bool
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
                    ds = xr.concat([ds_old, ds], "over_time")
                else:
                    logging.info("did not detect any historical data")

            logging.info("saving data to history cache")
            c[bench_cfg_hash] = ds
        return ds

    def setup_dataset(
        self, bench_cfg: BenchCfg, time_src: datetime | str
    ) -> tuple[BenchCfg, List, List]:
        """A function for generating an n-d xarray from a set of input variables in the BenchCfg

        Args:
            bench_cfg (BenchCfg): description of the benchmark parameters
            time_src (datetime | str): a representation of the sample time

        Returns:
            _type_: _description_
        """

        if time_src is None:
            time_src = datetime.now()
        bench_cfg.meta_vars = self.define_extra_vars(bench_cfg, bench_cfg.repeats, time_src)

        bench_cfg.all_vars = bench_cfg.input_vars + bench_cfg.meta_vars

        for i in bench_cfg.all_vars:
            logging.info(i.sampling_str(bench_cfg.debug))

        dims_cfg = DimsCfg(bench_cfg)
        function_inputs = list(
            zip(product(*dims_cfg.dim_ranges_index), product(*dims_cfg.dim_ranges))
        )
        # xarray stores K N-dimensional arrays of data.  Each array is named and in this case we have a nd array for each result variable
        data_vars = {}

        for rv in bench_cfg.result_vars:
            if type(rv) == ResultVar:
                result_data = np.empty(dims_cfg.dims_size)
                result_data.fill(np.nan)
                data_vars[rv.name] = (dims_cfg.dims_name, result_data)
            elif type(rv) == ResultVec:
                for i in range(rv.size):
                    result_data = np.full(dims_cfg.dims_size, np.nan)
                    data_vars[rv.index_name(i)] = (dims_cfg.dims_name, result_data)

        bench_cfg.ds = xr.Dataset(data_vars=data_vars, coords=dims_cfg.coords)
        bench_cfg.ds_dynamic = self.ds_dynamic

        return bench_cfg, function_inputs, dims_cfg.dims_name

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
            samples_debug=2 if repeats > 2 else 1,
            units="repeats",
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
    ) -> BenchCfg:
        """A function for generating an n-d xarray from a set of input variables in the BenchCfg

        Args:
            bench_cfg (BenchCfg): description of the benchmark parameters
            time_src (datetime): a representation of the sample time

        Returns:
            bench_cfg (BenchCfg): description of the benchmark parameters
        """
        bench_cfg, func_inputs, dims_name = self.setup_dataset(bench_cfg, time_src)
        constant_inputs = self.define_const_inputs(bench_cfg.const_vars)
        bench_cfg.hmap_kdims = sorted(dims_name)

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
                bench_cfg.tag,
            )
            job.setup_hashes()
            jobs.append(job)

            jid = f"{bench_cfg.title}:call {callcount}/{len(func_inputs)}"
            worker = partial(worker_kwargs_wrapper, self.worker, bench_cfg)
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
                self.store_results(result, bench_cfg, job, bench_run_cfg)

        if bench_run_cfg.executor != Executors.SERIAL:
            for job, res in zip(jobs, results_list):
                self.store_results(res, bench_cfg, job, bench_run_cfg)

        for inp in bench_cfg.all_vars:
            self.add_metadata_to_dataset(bench_cfg, inp)
        return bench_cfg

    def store_results(
        self,
        job_result: JobFuture,
        bench_cfg: BenchCfg,
        worker_job: WorkerJob,
        bench_run_cfg: BenchRunCfg,
    ) -> None:
        result = job_result.result()
        if result is not None:
            logging.info(f"{job_result.job.job_id}:")
            if bench_cfg.print_bench_inputs:
                for k, v in worker_job.function_input.items():
                    logging.info(f"\t {k}:{v}")

            result_dict = result if isinstance(result, dict) else result.param.values()

            for rv in bench_cfg.result_vars:
                result_value = result_dict[rv.name]
                if bench_run_cfg.print_bench_results:
                    logging.info(f"{rv.name}: {result_value}")

                if isinstance(rv, ResultVar):
                    set_xarray_multidim(bench_cfg.ds[rv.name], worker_job.index_tuple, result_value)
                elif isinstance(rv, ResultVec):
                    if isinstance(result_value, (list, np.ndarray)):
                        if len(result_value) == rv.size:
                            for i in range(rv.size):
                                set_xarray_multidim(
                                    bench_cfg.ds[rv.index_name(i)],
                                    worker_job.index_tuple,
                                    result_value[i],
                                )

                else:
                    raise RuntimeError("Unsupported result type")
            for rv in bench_cfg.result_hmaps:
                bench_cfg.hmaps[rv.name][worker_job.canonical_input] = result_dict[rv.name]

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

    def add_metadata_to_dataset(self, bench_cfg: BenchCfg, input_var: ParametrizedSweep) -> None:
        """Adds variable metadata to the xrarry so that it can be used to automatically plot the dimension units etc.

        Args:
            bench_cfg (BenchCfg):
            input_var (ParametrizedSweep): The varible to extract metadata from
        """

        for rv in bench_cfg.result_vars:
            if type(rv) == ResultVar:
                bench_cfg.ds[rv.name].attrs["units"] = rv.units
                bench_cfg.ds[rv.name].attrs["long_name"] = rv.name
            elif type(rv) == ResultVec:
                for i in range(rv.size):
                    bench_cfg.ds[rv.index_name(i)].attrs["units"] = rv.units
                    bench_cfg.ds[rv.index_name(i)].attrs["long_name"] = rv.name
            else:
                pass  # todo

        dsvar = bench_cfg.ds[input_var.name]
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
