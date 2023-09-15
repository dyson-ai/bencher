from typing import Any
import bencher as bch
import param 


class ExampleParam(bch.ParametrizedSweep):

    var_float = param.Number(bounds=(0, 10))
    var_int = param.Integer(bounds=[0, 100])

    result = bch.ResultVar()

    def __call__(self, **kwargs) -> Any:
        self.update_params_from_kwargs(**kwargs)
        return self.get_results_values_as_dict()


def bench_basic(run_cfg:bch.BenchRunCfg = bch.BenchRunCfg(),report:bch.BenchReport = bch.BenchReport):

    bench = bch.Bench("example_param",ExampleParam())

    bench.plot_sweep("basic")

    return bench




if __name__ == "__main__":
    bench_basic()