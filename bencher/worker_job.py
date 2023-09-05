from typing import List, Tuple
from dataclasses import dataclass, field
from sortedcontainers import SortedDict
from .utils import hash_sha1

from copy import deepcopy
import logging
#
# """
# create list of jobs
#     for each job
#             compute
#             cache result
#         append future

#     for future in futures:


# """


def worker_cached(self, bench_cfg , worker_job):
    function_input_deep = deepcopy(worker_job.function_input)
    #  function_input_deep = deepcopy(function_input)
    if not bench_cfg.pass_repeat:
        function_input_deep.pop("repeat")
    if "over_time" in function_input_deep:
        function_input_deep.pop("over_time")
    if "time_event" in function_input_deep:
        function_input_deep.pop("time_event")

    if self.worker_input_cfg is None:  # worker takes kwargs
        # result = self.worker(worker_job)
        result = self.worker(**function_input_deep)
    else:
        # worker takes a parametrised input object
        input_cfg = self.worker_input_cfg()
        for k, v in function_input_deep.items():
            input_cfg.param.set_param(k, v)

        result = self.worker(input_cfg)

    for msg in worker_job.msgs:
        logging.info(msg)
    if self.sample_cache is not None and not worker_job.found_in_cache:
        self.sample_cache.set(
            worker_job.function_input_signature_benchmark_context, result, tag=worker_job.tag
        )
        self.sample_cache.set(
            worker_job.function_input_signature_pure, result, tag=worker_job.tag
        )
    return result



@dataclass
class WorkerJob:
    function_input_vars: List
    index_tuple: Tuple[int]
    dims_name: List[str]
    constant_inputs: dict
    bench_cfg_sample_hash: str
    tag: str

    function_input: SortedDict = None
    fn_inputs_sorted: List[str] = None
    function_input_signature_pure: str = None
    function_input_signature_benchmark_context: str = None
    found_in_cache: bool = False
    msgs: List[str] = field(default_factory=list)

    def setup_hashes(self) -> None:
        self.function_input = SortedDict(zip(self.dims_name, self.function_input_vars))

        if self.constant_inputs is not None:
            self.function_input = self.function_input | self.constant_inputs

        # store a tuple of the inputs as keys for a holomap
        # the signature is the hash of the inputs to to the function + meta variables such as repeat and time + the hash of the benchmark sweep as a whole (without the repeats hash)
        self.fn_inputs_sorted = list(SortedDict(self.function_input).items())
        self.function_input_signature_pure = hash_sha1((self.fn_inputs_sorted, self.tag))

        self.function_input_signature_benchmark_context = hash_sha1(
            (self.function_input_signature_pure, self.bench_cfg_sample_hash)
        )

    # def call_worker(self,):
