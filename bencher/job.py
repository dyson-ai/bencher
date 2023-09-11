from typing import Callable
from dataclasses import dataclass
from sortedcontainers import SortedDict
from .utils import hash_sha1

import logging
from diskcache import Cache
from concurrent.futures import Future, ProcessPoolExecutor


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
        # self.cache =None
        self.tag = tag


@dataclass
class JobFuture:
    res: dict
    job_id: str

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

    def add_job(self, job: Job) -> JobFuture | Future:
        self.worker_wrapper_call_count += 1

        if self.cache is not None:
            if not self.overwrite and job.job_key in self.cache:
                logging.info(f"Found job: {job.job_id} in cache, loading...")
                # logging.info(f"Found key: {job.job_key} in cache")
                self.worker_cache_call_count += 1
                return JobFuture(self.cache[job.job_key], job.job_id)

        self.worker_fn_call_count += 1

        if self.executor is not None:
            self.overwrite_msg(job, " starting parallel job...")
            return self.executor.submit(run_job, job, self.cache)
        self.overwrite_msg(job, " starting serial job...")
        return JobFuture(run_job(job, self.cache), job.job_id)

    def overwrite_msg(self, job, suffix) -> None:
        if self.overwrite:
            # logging.info(f"Overwriting key: {job.job_key}{suffix}")
            logging.info(f"{job.job_id} OVERWRITING cache{suffix}")

        else:
            # logging.info(f"No key: {job.job_key} in cache{suffix}")
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
        logging.info(f"job calls: {self.worker_wrapper_call_count}")
        logging.info(f"cache calls: {self.worker_cache_call_count}")
        logging.info(f"worker calls: {self.worker_fn_call_count}")
        if self.cache:
            return f"cache size :{int(self.cache.volume() / 1000000)}MB / {int(self.size_limit/1000000)}MB"
        return ""


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
