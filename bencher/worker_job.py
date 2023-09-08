from typing import List, Tuple, Any
from dataclasses import dataclass, field
from sortedcontainers import SortedDict
from .utils import hash_sha1
from bencher.utils import hmap_canonical_input


@dataclass
class WorkerJob:
    function_input_vars: List
    index_tuple: Tuple[int]
    dims_name: List[str]
    constant_inputs: dict
    bench_cfg_sample_hash: str
    tag: str

    function_input: SortedDict = None
    canonical_input: Tuple[Any] = None
    fn_inputs_sorted: List[str] = None
    function_input_signature_pure: str = None
    function_input_signature_benchmark_context: str = None
    found_in_cache: bool = False
    msgs: List[str] = field(default_factory=list)

    def setup_hashes(self) -> None:
        self.function_input = SortedDict(zip(self.dims_name, self.function_input_vars))

        self.canonical_input = hmap_canonical_input(self.function_input)

        if self.constant_inputs is not None:
            self.function_input = self.function_input | self.constant_inputs

        # store a tuple of the inputs as keys for a holomap
        # the signature is the hash of the inputs to to the function + meta variables such as repeat and time + the hash of the benchmark sweep as a whole (without the repeats hash)
        self.fn_inputs_sorted = list(SortedDict(self.function_input).items())
        self.function_input_signature_pure = hash_sha1((self.fn_inputs_sorted, self.tag))

        self.function_input_signature_benchmark_context = hash_sha1(
            (self.function_input_signature_pure, self.bench_cfg_sample_hash)
        )
