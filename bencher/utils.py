from typing import Tuple, List
from bencher.bench_vars import ResultVar, ResultVec, ResultList, ResultSeries
from collections import namedtuple
import param


def make_namedtuple(class_name: str, **fields) -> namedtuple:
    """Convenience method for making a named tuple

    Args:
        class_name (str): name of the named tuple

    Returns:
        namedtuple: a named tuple with the fields as values
    """
    return namedtuple(class_name, fields)(*fields.values())


def update_params_from_kwargs(self, **kwargs) -> None:
    """Given a dictionary of kwargs, set the parameters of the passed class 'self' to the values in the dictionary."""
    used_params = {}
    for key in self.param.params().keys():
        if key in kwargs:
            if key != "name":
                used_params[key] = kwargs[key]

    self.param.update(**used_params)


def get_input_and_results(self, include_name: bool = False) -> Tuple[dict, dict]:
    """Get dictionaries of input parameters and result parameters

    Args:
        self: A parametrised class
        include_name (bool): Include the name parameter that all parametrised classes have. Default False

    Returns:
        Tuple[dict, dict]: a tuple containing the inputs and result parameters as dictionaries
    """
    inputs = {}
    results = {}
    for k, v in self.param.params().items():
        if isinstance(v, (ResultList, ResultSeries, ResultVar, ResultVec)):
            results[k] = v
        else:
            inputs[k] = v

    if not include_name:
        inputs.pop("name")
    return make_namedtuple("inputresult", inputs=inputs, results=results)


def get_inputs_only(self) -> List[param.Parameter]:
    """Return a list of input parameters

    Returns:
        List[param.Parameter]: A list of input parameters
    """
    return list(get_input_and_results(self).inputs.values())


def get_results_only(self) -> List[param.Parameter]:
    """Return a list of input parameters

    Returns:
        List[param.Parameter]: A list of result parameters
    """
    return list(get_input_and_results(self).results.values())


def get_results_values_as_dict(self) -> dict:
    """Get a dictionary of result variables with the name and the current value"""
    values = self.param.values()
    return {key: values[key] for key in get_input_and_results(self).results}
