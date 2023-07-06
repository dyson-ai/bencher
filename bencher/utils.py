from typing import List
from bencher.bench_vars import ResultVar, ResultVec, ResultList, ResultSeries


def update_params_from_kwargs(self, **kwargs):
    used_params = {}
    for key in self.param.params().keys():
        if key in kwargs:
            if key != "name":
                used_params[key] = kwargs[key]

    self.param.update(**used_params)


def get_input_and_results(self) -> List:
    inputs = {}
    results = {}
    for k, v in self.param.params().items():
        if (
            isinstance(v, ResultVar)
            or isinstance(v, ResultVec)
            or isinstance(v, ResultList)
            or isinstance(v, ResultSeries)
        ):
            results[k] = v
        else:
            inputs[k] = v
    return inputs, results


def get_inputs_only(self) -> List:
    return get_input_and_results(self)[0].values()


def get_results_as_dict(self) -> dict:
    values = self.param.values()
    return {key: values[key] for key in get_input_and_results(self)[1]}
