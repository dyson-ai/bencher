# you need this import to be able to reference a class from a static method in that class
from __future__ import annotations

import math
from pickle import PicklingError, UnpicklingError
from typing import Type

# """This file has some examples for how to perform basic benchmarking parameter sweeps"""
from bencher import Bench, BenchRunCfg, BoolSweep, FloatSweep, ParametrizedSweep
from bencher.example.benchmark_data import ExampleBenchCfgOut


class ExpensiveNonPickleableResource:
    """This represents a global resource that is expensive to setup and teardown and is not serialisable e.g. (A simulator,a connection to a piece of real world hardware etc.)"""

    def __init__(self) -> None:
        self.id = None

    def __getstate__(self) -> Type[PicklingError]:
        """Make sure this is not pickleable"""
        raise PicklingError

    def __setstate__(self, from_state) -> Type[UnpicklingError]:
        """Make sure this is not pickleable"""
        raise UnpicklingError

    def setup(self) -> None:
        print("setup expensive resource")
        self.id = 1

    def shutdown(self) -> None:
        print("shutdown expensive resource once")
        self.id = None


# set up as a global variable as it is truely global (i.e real world hardware).  Great care must be taken that the state of this global variable does not corrupt the results of bencher. All meaningful state should be put into an input config so that it can be tracked properly across parameter sweeps


class InputCfg(ParametrizedSweep):
    """A class that has 1 input parameter, but the benchmark function depends on a global resource"""

    theta = FloatSweep(
        default=1,
        bounds=[0, 10],
        doc="The standard deviation of the noise",
        units="v",
    )

    modify_global = BoolSweep(doc="Use global state as part of the function callback")


class GlobalResource:
    def __init__(self):
        self.expensive_res = ExpensiveNonPickleableResource()
        self.expensive_res.setup()

    def shutdown(self):
        self.expensive_res.shutdown()

    def benchmark_function(self, input_cfg: InputCfg) -> ExampleBenchCfgOut:
        output = ExampleBenchCfgOut()
        output.out_sin = math.sin(input_cfg.theta) + self.expensive_res.id
        if input_cfg.modify_global:
            self.expensive_res.id += 1
        return output


def example_persistent(run_cfg: BenchRunCfg) -> Bench:
    """This example shows how maintain a peristent object across runs. This could be useful for resources that are expensive to start up and shut down that can be shared across different function calls during benchmarking. This resource may not be picklable.

    Args:
        run_cfg (BenchRunCfg): configuration of how to perform the param sweep

    Returns:
        Bench: results of the parameter sweep
    """

    # set up the expensive resource once
    res = GlobalResource()

    bencher = Bench("benchmarking_example_float1D", res.benchmark_function, InputCfg)

    bencher.plot_sweep(
        title="Example 1D Float",
        input_vars=[InputCfg.param.theta, InputCfg.param.modify_global],
        result_vars=[ExampleBenchCfgOut.param.out_sin],
        description=example_persistent.__doc__,
        run_cfg=run_cfg,
    )
    # shutdown the resource at the end
    res.shutdown()

    return bencher


if __name__ == "__main__":
    ex_run_cfg = BenchRunCfg()

    example_persistent(ex_run_cfg).plot()
