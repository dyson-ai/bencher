from typing import Callable
from dataclasses import dataclass
from sortedcontainers import SortedDict
from .utils import hash_sha1

import logging
from diskcache import Cache
from concurrent.futures import Future, ProcessPoolExecutor


# @dataclass
class Job:
    # id:str
    # kwargs:dict
    # function:Callable
    # result:dict

    def __init__(
        self, job_id: str, function: Callable, job_args: dict, job_key=None, tag=""
    ) -> None:
        self.job_id = job_id
        self.function = function
        self.job_args = job_args
        if job_key is None:
            self.job_key = hash_sha1(tuple(SortedDict(self.job_args).items()))
        else:
            self.job_key = job_key
        # self.cache =None
        self.tag = tag

    # def run_job(self) -> None:
    # self.result = self.function(self.kwargs)


@dataclass
class JobFuture:
    res: dict

    def result(self):
        return self.res


def run_job(job: Job, cache: Cache):
    # logging.info(f"starting job:{job.job_id}")
    result = job.function(**job.job_args)
    # logging.info(f"finished job:{job.job_id}")
    if cache is not None:
        cache.set(job.job_key, result, tag=job.tag)
    return result


class JobCache:
    def __init__(
        self,
        parallel: bool = False,
        overwrite: bool = True,
        cache_name: str = "fcache",
        tag_index: bool = True,
        size_limit: int = int(100e8),
        use_cache=True,
    ):
        if use_cache:
            self.cache = Cache(f"cachedir/{cache_name}", tag_index=tag_index, size_limit=size_limit)
            logging.info(f"cache dir: {self.cache.directory}")

        else:
            self.cache = None
        if parallel:
            self.executor = ProcessPoolExecutor()
        else:
            self.executor = None

        self.overwrite = overwrite

        self.call_count = 0
        self.size_limit = size_limit

        self.worker_wrapper_call_count = 0
        self.worker_fn_call_count = 0
        self.worker_cache_call_count = 0

    def add_job(self, job: Job, overwrite=False) -> JobFuture | Future:
        self.worker_wrapper_call_count += 1

        if self.cache is not None:
            if not overwrite and job.job_key in self.cache:
                logging.info(f"Found job: {job.job_id} in cache, loading...")
                logging.info(f"Found key: {job.job_key} in cache")

                self.worker_cache_call_count += 1
                return JobFuture(self.cache[job.job_key])

        self.worker_fn_call_count += 1

        if self.executor is not None:
            self.overwrite_msg(job, overwrite, " starting parallel job...")
            return self.executor.submit(run_job, job, self.cache)
        self.overwrite_msg(job, overwrite, " starting serial job...")
        return JobFuture(run_job(job, self.cache))

    def overwrite_msg(self, job, overwrite, suffix) -> None:
        if overwrite:
            logging.info(f"Overwriting key: {job.job_key}{suffix}")
            logging.info(f"{job.job_id} OVERWRITING cache{suffix}")

        else:
            logging.info(f"No key: {job.job_key} in cache{suffix}")
            logging.info(f"{job.job_id} NOT in cache{suffix}")

    def clear_call_counts(self) -> None:
        """Clear the worker and cache call counts, to help debug and assert caching is happening properly"""
        self.worker_wrapper_call_count = 0
        self.worker_fn_call_count = 0
        self.worker_cache_call_count = 0

    def clear(self) -> None:
        if self.cache:
            self.cache.clear()

    def clear_tag(self, tag: str) -> None:
        logging.info(f"clearing the sample cache for tag: {tag}")
        removed_vals = self.cache.evict(tag)
        logging.info(f"removed: {removed_vals} items from the cache")

    def close(self) -> None:
        if self.cache:
            self.cache.close()

    def stats(self) -> str:
        if self.cache:
            return f"cache size :{int(self.cache.volume() / 1000000)}MB / {int(self.size_limit/1000000)}MB"
        return ""


# logging.info(f"pure: {function_input_signature_pure}")
# if (
#     not bench_cfg.overwrite_sample_cache
#     and worker_job.function_input_signature_benchmark_context in self.sample_cache
# ):
#     result = self.sample_cache[worker_job.function_input_signature_benchmark_context]
#     worker_job.found_in_cache = True
#     worker_job.msgs.append(
#         f"Hash: {worker_job.function_input_signature_benchmark_context} was found in context cache, loading..."
#     )
#     self.worker_cache_call_count += 1
# elif (
#     not bench_cfg.overwrite_sample_cache
#     and bench_run_cfg.only_hash_tag
#     and (worker_job.function_input_signature_pure in self.sample_cache)
# ):
#     worker_job.msgs.append(
#         f"Hash: {worker_job.function_input_signature_benchmark_context} not found in context cache"
#     )
#     worker_job.msgs.append(
#         f"Hash: {worker_job.function_input_signature_pure} was found in the function cache, loading..."
#     )

#     result = self.sample_cache[worker_job.function_input_signature_pure]
#     worker_job.found_in_cache = True
#     self.worker_cache_call_count += 1
# else:
#     worker_job.msgs.append(
#         f"Context not in cache: {worker_job.function_input_signature_benchmark_context}"
#     )
#     worker_job.msgs.append(
#         f"Function inputs not cache: {worker_job.function_input_signature_pure}"
#     )
#     worker_job.msgs.append("Calling benchmark function")
#     result = self.worker_wrapper(bench_cfg, worker_job, executor)


class JobFunctionCache(JobCache):
    def __init__(
        self,
        function: Callable,
        overwrite=False,
        parallel: bool = False,
        cache_name: str = "fcache",
        tag_index: bool = True,
        size_limit: int = int(100e8),
    ):
        super().__init__(
            parallel=parallel,
            cache_name=cache_name,
            tag_index=tag_index,
            size_limit=size_limit,
            overwrite=overwrite,
        )
        self.function = function

    def call(self, **kwargs) -> JobFuture | Future:
        return self.add_job(Job(self.call_count, self.function, kwargs))


# # #
# # """
# # create list of jobs
# #     for each job
# #             compute
# #             cache result
# #         append future

# #     for future in futures:


# # """


# # def run_cached(function:Callable,**kwargs):
# # results =function(**kwargs)


# def worker_cached(self, bench_cfg, worker_job):
#     function_input_deep = deepcopy(worker_job.function_input)
#     #  function_input_deep = deepcopy(function_input)
#     if not bench_cfg.pass_repeat:
#         function_input_deep.pop("repeat")
#     if "over_time" in function_input_deep:
#         function_input_deep.pop("over_time")
#     if "time_event" in function_input_deep:
#         function_input_deep.pop("time_event")

#     if self.worker_input_cfg is None:  # worker takes kwargs
#         # result = self.worker(worker_job)
#         result = self.worker(**function_input_deep)
#     else:
#         # worker takes a parametrised input object
#         input_cfg = self.worker_input_cfg()
#         for k, v in function_input_deep.items():
#             input_cfg.param.set_param(k, v)

#         result = self.worker(input_cfg)

#     for msg in worker_job.msgs:
#         logging.info(msg)
#     if self.sample_cache is not None and not worker_job.found_in_cache:
#         self.sample_cache.set(
#             worker_job.function_input_signature_benchmark_context, result, tag=worker_job.tag
#         )
#         self.sample_cache.set(worker_job.function_input_signature_pure, result, tag=worker_job.tag)
#     return result


# @dataclass
# class WorkerJob:
#     function_input_vars: List
#     index_tuple: Tuple[int]
#     dims_name: List[str]
#     constant_inputs: dict
#     bench_cfg_sample_hash: str
#     tag: str

#     function_input: SortedDict = None
#     fn_inputs_sorted: List[str] = None
#     function_input_signature_pure: str = None
#     function_input_signature_benchmark_context: str = None
#     found_in_cache: bool = False
#     msgs: List[str] = field(default_factory=list)

#     def setup_hashes(self) -> None:
#         self.function_input = SortedDict(zip(self.dims_name, self.function_input_vars))

#         if self.constant_inputs is not None:
#             self.function_input = self.function_input | self.constant_inputs

#         # store a tuple of the inputs as keys for a holomap
#         # the signature is the hash of the inputs to to the function + meta variables such as repeat and time + the hash of the benchmark sweep as a whole (without the repeats hash)
#         self.fn_inputs_sorted = list(SortedDict(self.function_input).items())
#         self.function_input_signature_pure = hash_sha1((self.fn_inputs_sorted, self.tag))

#         self.function_input_signature_benchmark_context = hash_sha1(
#             (self.function_input_signature_pure, self.bench_cfg_sample_hash)
#         )

#     # def call_worker(self,):
