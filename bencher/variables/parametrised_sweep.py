from datetime import datetime
from enum import Enum, auto
from typing import List, Tuple

import numpy as np
import param
from pandas import Timestamp
from param import Boolean, Integer, Number, Parameterized, Selector
from strenum import StrEnum
import holoviews as hv
import panel as pn
from bencher.utils import make_namedtuple, hash_sha1


class ParametrizedSweep(Parameterized):
    """Parent class for all Sweep types that need a custom hash"""

    @staticmethod
    def param_hash(
        param_type: Parameterized, hash_value: bool = True, hash_meta: bool = False
    ) -> int:
        """A custom hash function for parametrised types with options for hashing the value of the type and hashing metadata

        Args:
            param_type (Parameterized): A parameter
            hash_value (bool, optional): use the value as part of the hash. Defaults to True.
            hash_meta (bool, optional): use metadata as part of the hash. Defaults to False.

        Returns:
            int: a hash
        """

        curhash = 0
        if hash_value:
            for k, v in param_type.param.values().items():
                if k != "name":
                    curhash = hash_sha1((curhash, hash_sha1(v)))

        if hash_meta:
            for k, v in param_type.param.params().items():
                if k != "name":
                    print(f"key:{k}, hash:{hash_sha1(k)}")
                    print(f"value:{v}, hash:{hash_sha1(v)}")
                    curhash = hash_sha1((curhash, hash_sha1(k), hash_sha1(v)))
        return curhash

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return ParametrizedSweep.param_hash(self, True, False)

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

    def get_results_values_as_dict(self, holomap=None) -> dict:
        """Get a dictionary of result variables with the name and the current value"""
        values = self.param.values()
        output = {key: values[key] for key in self.get_input_and_results().results}
        if holomap is not None:
            output |= {"hmap": holomap}
        return output

    def get_inputs_only(self) -> List[param.Parameter]:
        """Return a list of input parameters

        Returns:
            List[param.Parameter]: A list of input parameters
        """
        return list(self.get_input_and_results().inputs.values())

    def get_results_only(self) -> List[param.Parameter]:
        """Return a list of input parameters

        Returns:
            List[param.Parameter]: A list of result parameters
        """
        return list(self.get_input_and_results(self).results.values())

    def get_inputs_as_dims(
        self, compute_values=False, remove_dims: str | List[str] = None
    ) -> List[hv.Dimension]:
        inputs = self.get_inputs_only()

        if remove_dims is not None:
            if type(remove_dims) == str:
                remove_dims = [remove_dims]
            filtered_inputs = [i for i in inputs if i.name not in remove_dims]
            inputs = filtered_inputs

        return [iv.as_dim(compute_values) for iv in inputs]

    def to_dynamic_map(
        self,
        callback=None,
        name=None,
        remove_dims: str | List[str] = None,
    ) -> hv.DynamicMap:
        if callback is None:
            callback = self.call

        def callback_wrapper(**kwargs):
            return callback(**kwargs)["hmap"]

        return hv.DynamicMap(
            callback=callback_wrapper,
            kdims=self.get_inputs_as_dims(compute_values=False, remove_dims=remove_dims),
            name=name,
        ).opts(shared_axes=False, framewise=True, width=1000, height=1000)

    def to_holomap(self, callback, remove_dims: str | List[str] = None) -> hv.DynamicMap:
        return hv.HoloMap(
            hv.DynamicMap(
                callback=callback,
                kdims=self.get_inputs_as_dims(compute_values=True, remove_dims=remove_dims),
            )
        )
        # return hv.HoloMap(self.to_dynamic_map(callback=callback, remove_dims=remove_dims))
        # return hv.DynamicMap(
        #     kdims=self.get_inputs_as_dims(compute_values=True, remove_dims=remove_dims)
        # )

    def call(self):
        pass

    def plot_hmap(self, **kwargs):
        return self.call(**kwargs)["hmap"]
