#!/usr/bin/env python3

from diskcache import Cache
from concurrent.futures import ProcessPoolExecutor,Future
from typing import Callable
from sortedcontainers import SortedDict
from typing import Any
import hashlib


def hash_sha1(var: Any) -> str:
    """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
    return hashlib.sha1(str(var).encode("ASCII")).hexdigest()


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

class JobFuture:
    def __init__(self, job_id: str, job_result: dict = None, future: Future = None) -> None:
        self.job_id = job_id
        self.job_result = job_result
        self.future = future
        # either a result or a future needs to be passed
        assert self.job_result is not None or self.future is not None

    def result(self):
        if self.future is not None:
            return self.future.result()
        return self.job_result


def worker(**kwargs) -> dict:
    return kwargs


def run_job(job: Job, cache: Cache) -> dict:
    result = job.function(**job.job_args)
    if cache is not None:
        cache.set(job.job_key, result, tag=job.tag)
    return result


class JobCache:
    def __init__(
        self,
        cache_name: str = "func_cache",
        tag_index: bool = True,
        size_limit: int = int(100e8),
    ):
        self.cache = Cache(f"cachedir/{cache_name}", tag_index=tag_index, size_limit=size_limit)
        self.executor = ProcessPoolExecutor()

    def add_job(self, job: Job) -> dict:
        if job.job_key in self.cache:
            return JobFuture(job_id=job.job_id, job_result=self.cache[job.job_key])
        return JobFuture(
                job_id=job.job_id, future=self.executor.submit(run_job, job, self.cache)
            )


if __name__ == "__main__":
    for m in range(100):
        jc = JobCache()

        job_futures = []
        for i in range(1000):
            job_futures.append(jc.add_job(Job(str(i), worker, dict(i=i))))

        for fut in job_futures:
            print(fut.result())
