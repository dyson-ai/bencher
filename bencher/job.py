from __future__ import annotations
from typing import Callable
from sortedcontainers import SortedDict
import logging
from diskcache import Cache
from concurrent.futures import Future, ProcessPoolExecutor
from .utils import hash_sha1
from strenum import StrEnum
from enum import auto

try:
    from scoop import futures as scoop_future_executor
except ImportError as e:
    logging.warning(e.msg)
    scoop_future_executor = None


class Job:
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
        self.tag = tag


# @dataclass
class JobFuture:
    def __init__(self, job: Job, res: dict = None, future: Future = None, cache=None) -> None:
        self.job = job
        self.res = res
        self.future = future
        # either a result or a future needs to be passed
        assert self.res is not None or self.future is not None
        self.cache = cache

    def result(self):
        if self.future is not None:
            self.res = self.future.result()
        if self.cache is not None and self.res is not None:
            self.cache.set(self.job.job_key, self.res, tag=self.job.tag)
        return self.res


def run_job(job: Job) -> dict:
    result = job.function(**job.job_args)
    return result


class Executors(StrEnum):
    SERIAL = auto()  # slow but reliable
    MULTIPROCESSING = auto()  # breaks for large number of futures
    SCOOP = auto()  # requires running with python -m scoop your_file.py
    # THREADS=auto() #not that useful as most bench code is cpu bound

    @staticmethod
    def factory(provider: Executors) -> Future():
        providers = {
            Executors.SERIAL: None,
            Executors.MULTIPROCESSING: ProcessPoolExecutor(),
            Executors.SCOOP: scoop_future_executor,
        }
        return providers[provider]


class FutureCache:
    """The aim of this class is to provide a unified interface for running jobs.  T"""

    def __init__(
        self,
        executor=Executors.SERIAL,
        overwrite: bool = True,
        cache_name: str = "fcache",
        tag_index: bool = True,
        size_limit: int = int(20e9),  # 20 GB
        use_cache=True,
    ):
        self.executor = Executors.factory(executor)
        if use_cache:
            self.cache = Cache(f"cachedir/{cache_name}", tag_index=tag_index, size_limit=size_limit)
            logging.info(f"cache dir: {self.cache.directory}")
        else:
            self.cache = None

        self.overwrite = overwrite
        self.call_count = 0
        self.size_limit = size_limit

        self.worker_wrapper_call_count = 0
        self.worker_fn_call_count = 0
        self.worker_cache_call_count = 0

    def submit(self, job: Job) -> JobFuture:
        self.worker_wrapper_call_count += 1

        if self.cache is not None:
            if not self.overwrite and job.job_key in self.cache:
                logging.info(f"Found job: {job.job_id} in cache, loading...")
                # logging.info(f"Found key: {job.job_key} in cache")
                self.worker_cache_call_count += 1
                return JobFuture(
                    job=job,
                    res=self.cache[job.job_key],
                )

        self.worker_fn_call_count += 1

        if self.executor is not None:
            self.overwrite_msg(job, " starting parallel job...")
            return JobFuture(
                job=job,
                future=self.executor.submit(run_job, job),
                cache=self.cache,
            )
        self.overwrite_msg(job, " starting serial job...")
        return JobFuture(
            job=job,
            res=run_job(job),
            cache=self.cache,
        )

    def overwrite_msg(self, job: Job, suffix: str) -> None:
        msg = "OVERWRITING" if self.overwrite else "NOT in"
        logging.info(f"{job.job_id} {msg} cache{suffix}")

    def clear_call_counts(self) -> None:
        """Clear the worker and cache call counts, to help debug and assert caching is happening properly"""
        self.worker_wrapper_call_count = 0
        self.worker_fn_call_count = 0
        self.worker_cache_call_count = 0

    def clear_cache(self) -> None:
        if self.cache:
            self.cache.clear()

    def clear_tag(self, tag: str) -> None:
        logging.info(f"clearing the sample cache for tag: {tag}")
        removed_vals = self.cache.evict(tag)
        logging.info(f"removed: {removed_vals} items from the cache")

    def close(self) -> None:
        if self.cache:
            self.cache.close()
        if self.executor:
            self.executor.shutdown()

    # def __del__(self):
    #     self.close()

    def stats(self) -> str:
        logging.info(f"job calls: {self.worker_wrapper_call_count}")
        logging.info(f"cache calls: {self.worker_cache_call_count}")
        logging.info(f"worker calls: {self.worker_fn_call_count}")
        if self.cache:
            return f"cache size :{int(self.cache.volume() / 1000000)}MB / {int(self.size_limit/1000000)}MB"
        return ""


class JobFunctionCache(FutureCache):
    def __init__(
        self,
        function: Callable,
        overwrite=False,
        executor: bool = False,
        cache_name: str = "fcache",
        tag_index: bool = True,
        size_limit: int = int(100e8),
    ):
        super().__init__(
            executor=executor,
            cache_name=cache_name,
            tag_index=tag_index,
            size_limit=size_limit,
            overwrite=overwrite,
        )
        self.function = function

    def call(self, **kwargs) -> JobFuture:
        return self.submit(Job(self.call_count, self.function, kwargs))
