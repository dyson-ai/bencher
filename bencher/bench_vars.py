# pylint: skip-file
import hashlib
import re
from datetime import datetime
from enum import Enum, auto
from typing import List, Tuple

import numpy as np
import param
from pandas import Timestamp
from param import Boolean, Integer, Number, Parameterized, Selector
from strenum import StrEnum
import holoviews as hv
from collections import namedtuple


def hash_sha1(var: any) -> str:
    """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
    return hashlib.sha1(str(var).encode("ASCII")).hexdigest()


def capitalise_words(message: str):
    """Given a string of lowercase words, capitalise them

    Args:
        message (str): lower case string

    Returns:
        _type_: capitalised string
    """
    capitalized_message = " ".join([word.capitalize() for word in message.split(" ")])
    return capitalized_message


def un_camel(camel: str) -> str:
    """Given a snake_case string return a CamelCase string

    Args:
        camel (str): camelcase string

    Returns:
        str: uncamelcased string
    """

    return capitalise_words(re.sub("([a-z])([A-Z])", r"\g<1> \g<2>", camel.replace("_", " ")))


def param_hash(param_type: Parameterized, hash_value: bool = True, hash_meta: bool = False) -> int:
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


def make_namedtuple(class_name: str, **fields) -> namedtuple:
    """Convenience method for making a named tuple

    Args:
        class_name (str): name of the named tuple

    Returns:
        namedtuple: a named tuple with the fields as values
    """
    return namedtuple(class_name, fields)(*fields.values())


def as_dim(self, compute_values=False) -> hv.Dimension:
    """Takes a sweep variable and turns it into a holoview dimension

    Returns:
        hv.Dimension:
    """
    if hasattr(self, "bounds"):
        if compute_values:
            return hv.Dimension(
                (self.name, self.name),
                range=tuple(self.bounds),
                unit=self.units,
                values=self.values(False),
            )

        return hv.Dimension(
            (self.name, self.name),
            range=tuple(self.bounds),
            unit=self.units,
            default=self.default,
        )
    return hv.Dimension(
        (self.name, self.name),
        unit=self.units,
        values=self.values(False),
        default=self.default,
    )


class ParametrizedSweep(Parameterized):
    """Parent class for all Sweep types that need a custom hash"""

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return param_hash(self, True, False)

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

    def get_inputs_as_dims(self, compute_values=False):
        return [iv.as_dim(compute_values) for iv in self.get_inputs_only()]


# slots that are shared across all Sweep classes
# param does not work with multiple inheritance so define here
shared_slots = ["units", "samples", "samples_debug"]


def sweep_hash(parameter: Parameterized) -> int:
    """Generate a hash for a sweep variable

    Returns:
        int: hash
    """
    curhash = 0
    for v in parameter.values():
        print(f"value:{v}, hash:{hash_sha1(v)}")
        curhash = hash_sha1((curhash, hash_sha1(v)))
    return curhash


def hash_extra_vars(parameter: Parameterized) -> int:
    """hash extra meta vars in the parameter

    Args:
        parameter (Parameterized): a parameter

    Returns:
        int: hash
    """
    return hash_sha1((parameter.units, parameter.samples, parameter.samples_debug))


def describe_variable(v: Parameterized, debug: bool, include_samples: bool) -> List[str]:
    """Generate a string description of a variable

    Args:
        v (param.Parameterized): parameter to describe
        debug (bool): Generate a reduced number of samples from the variable
        include_samples (bool): Include a description of the samples

    Returns:
        str: String description of the variable
    """
    indent = "    "
    sampling_str = []
    sampling_str.append(f"{v.name}:")
    if include_samples:
        sampling_str.append(f"{indent}{v.sampling_str(debug)}")
    sampling_str.append(f"{indent}units: [{v.units}]")
    if v.doc is not None:
        sampling_str.append(f"{indent}docs: {v.doc}")
    for i in range(len(sampling_str)):
        sampling_str[i] = f"{indent}{sampling_str[i]}"
    return sampling_str


class BoolSweep(Boolean):
    """A class to reprsent a parameter sweep of bools"""

    __slots__ = shared_slots

    def __init__(self, units: str = "ul", samples: int = None, samples_debug: int = 2, **params):
        Boolean.__init__(self, **params)
        self.units = units
        if samples is None:
            self.samples = 2
        self.samples_debug = samples_debug

    def values(self, debug=False) -> List[bool]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        print(self.sampling_str(debug))
        return [True, False]

    def sampling_str(self, debug: bool) -> str:
        """Generate a string representation of the sampling procedure"""
        return f"sampling {self.name} from: [True,False]"

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_extra_vars(self)

    def as_dim(self, compute_values=False) -> hv.Dimension:
        return as_dim(self, compute_values=compute_values)


class TimeBase(Selector):
    """A class to capture a time snapshot of benchmark values.  Time is reprented as a continous value i.e a datetime which is converted into a np.datetime64.  To represent time as a discrete value use the TimeEvent class. The distinction is because holoview and plotly code makes different assumptions about discrete vs continous variables"""

    __slots__ = shared_slots

    def values(self, debug=False) -> List[str]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        print(self.sampling_str(debug))
        return self.objects

    def sampling_str(self, debug: bool) -> str:
        """Generate a string representation of the time sample

        Args:
            debug (bool): If true then self.samples_debug is used
        """
        return f"sampling from [The Past to {self.objects[0]}]"

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_extra_vars(self)


class TimeSnapshot(TimeBase):
    """A class to capture a time snapshot of benchmark values.  Time is reprented as a continous value i.e a datetime which is converted into a np.datetime64.  To represent time as a discrete value use the TimeEvent class. The distinction is because holoview and plotly code makes different assumptions about discrete vs continous variables"""

    __slots__ = shared_slots

    def __init__(
        self,
        datetime_src: datetime | str,
        units: str = "time",
        samples: int = None,
        samples_debug: int = 2,
        **params,
    ):
        if type(datetime_src) == str:
            Selector.__init__(self, [datetime_src], instantiate=True, **params)
        else:
            Selector.__init__(
                self,
                [Timestamp(datetime_src)],
                instantiate=True,
                **params,
            )
        self.units = units
        if samples is None:
            self.samples = len(self.objects)
        else:
            self.samples = samples
        self.samples_debug = min(self.samples, samples_debug)


class TimeEvent(TimeBase):
    """A class to represent a discrete event in time where the data was captured i.e a series of pull requests.  Here time is discrete and can't be interpolated, to represent time as a continous value use the TimeSnapshot class.  The distinction is because holoview and plotly code makes different assumptions about discrete vs continous variables"""

    __slots__ = shared_slots

    def __init__(
        self,
        time_event: str,
        units: str = "event",
        samples: int = None,
        samples_debug: int = 2,
        **params,
    ):
        Selector.__init__(
            self,
            [time_event],
            instantiate=True,
            **params,
        )
        self.units = units
        if samples is None:
            self.samples = len(self.objects)
        else:
            self.samples = samples
        self.samples_debug = min(self.samples, samples_debug)


class StringSweep(Selector):
    """A class to reprsent a parameter sweep of strings"""

    __slots__ = shared_slots

    def __init__(
        self,
        string_list: List[str],
        units: str = "ul",
        samples: int = None,
        samples_debug: int = 2,
        **params,
    ):
        Selector.__init__(self, string_list, instantiate=True, **params)
        self.units = units
        if samples is None:
            self.samples = len(self.objects)
        else:
            self.samples = samples
        self.samples_debug = min(self.samples, samples_debug)

    def values(self, debug=False) -> List[str]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        print(self.sampling_str(debug))
        return self.objects

    def sampling_str(self, debug: bool) -> str:
        """Generate a string representation of the of the sampling procedure

        Args:
            debug (bool): If true then self.samples_debug is used
        """
        object_str = ",".join([i for i in self.objects])
        return f"sampling {self.name} from: [{object_str}]"

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_extra_vars(self)


class EnumSweep(Selector):
    """A class to reprsent a parameter sweep of enums"""

    __slots__ = shared_slots

    def __init__(
        self, enum_type: Enum | List[Enum], units="ul", samples=None, samples_debug=2, **params
    ):
        # The enum can either be an Enum type or a list of enums
        list_of_enums = type(enum_type) is list
        if list_of_enums:
            selector_list = enum_type  # already a list of enums
        else:
            # create a list of enums from the enum type definition
            selector_list = [e for e in enum_type]
        Selector.__init__(self, selector_list, **params)
        if not list_of_enums:  # Grab the docs from the enum type def
            self.doc = enum_type.__doc__
        self.units = units
        if samples is None:
            self.samples = len(self.objects)
        else:
            self.samples = samples
        self.samples_debug = min(self.samples, samples_debug)

    def values(self, debug=False) -> List[Enum]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        print(self.sampling_str(debug))
        return self.objects

    def sampling_str(self, debug: bool) -> str:
        """Generate a string representation of the of the sampling procedure

        Args:
            debug (bool): If true then self.samples_debug is used
        """
        object_str = ",".join([i for i in self.objects])
        return f"sampling {self.name} from: [{object_str}]"

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_extra_vars(self)

    def as_dim(self, compute_values=False) -> hv.Dimension:
        return as_dim(self, compute_values=compute_values)


def int_float_sampling_str(name, samples) -> str:
    """Generate a string representation of the of the sampling procedure

    Args:
        debug (bool): If true then self.samples_debug is used
    """

    return f"sampling {name} from {samples} in {len(samples)} samples"


class IntSweep(Integer):
    """A class to reprsent a parameter sweep of ints"""

    __slots__ = shared_slots + ["sample_values"]

    def __init__(self, units="ul", samples=None, samples_debug=2, sample_values=None, **params):
        Integer.__init__(self, **params)
        self.units = units
        self.samples_debug = samples_debug

        if sample_values is None:
            if samples is None:
                if self.bounds is None:
                    raise RuntimeError("You must define bounds for integer types")
                else:
                    self.samples = 1 + self.bounds[1] - self.bounds[0]
            else:
                self.samples = samples
            self.sample_values = None
        else:
            self.sample_values = sample_values
            self.samples = len(self.sample_values)
            if "default" not in params:
                self.default = sample_values[0]

    def values(self, debug=False) -> List[int]:
        """return all the values for a parameter sweep.  If debug is true return the  list"""
        samps = self.samples_debug if debug else self.samples

        if self.sample_values is None:
            return [
                int(i)
                for i in np.linspace(
                    self.bounds[0], self.bounds[1], samps, endpoint=True, dtype=int
                )
            ]
        else:
            if debug:
                indices = [
                    int(i)
                    for i in np.linspace(
                        0, len(self.sample_values) - 1, self.samples_debug, dtype=int
                    )
                ]
                return [self.sample_values[i] for i in indices]
            else:
                return self.sample_values

    def sampling_str(self, debug: bool) -> str:
        """Generate a string representation of the of the sampling procedure

        Args:
        debug (bool): If true then self.samples_debug is used
        """
        return int_float_sampling_str(self.name, self.values(debug))

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_extra_vars(self)

    def as_dim(self, compute_values=False) -> hv.Dimension:
        return as_dim(self, compute_values=compute_values)

    ###THESE ARE COPIES OF INTEGER VALIDATION BUT ALSO ALLOW NUMPY INT TYPES
    def _validate_value(self, val, allow_None):
        if callable(val):
            return

        if allow_None and val is None:
            return

        if not isinstance(val, (int, np.integer)):
            raise ValueError(
                "Integer parameter %r must be an integer, " "not type %r." % (self.name, type(val))
            )

    ###THESE ARE COPIES OF INTEGER VALIDATION BUT ALSO ALLOW NUMPY INT TYPES
    def _validate_step(self, val, step):
        if step is not None and not isinstance(step, (int, np.integer)):
            raise ValueError(
                "Step can only be None or an " "integer value, not type %r" % type(step)
            )


class FloatSweep(Number):
    """A class to represent a parameter sweep of floats"""

    __slots__ = shared_slots + ["sample_values"]

    def __init__(self, units="ul", samples=10, samples_debug=2, sample_values=None, **params):
        Number.__init__(self, **params)
        self.units = units
        self.samples_debug = samples_debug
        if sample_values is None:
            self.samples = samples
            self.sample_values = None
        else:
            self.sample_values = sample_values
            self.samples = len(self.sample_values)
            if "default" not in params:
                self.default = sample_values[0]

    def values(self, debug=False) -> List[float]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        samps = self.samples_debug if debug else self.samples
        if self.sample_values is None:
            return np.linspace(self.bounds[0], self.bounds[1], samps)
        else:
            if debug:
                indices = [
                    int(i)
                    for i in np.linspace(
                        0, len(self.sample_values) - 1, self.samples_debug, dtype=int
                    )
                ]
                return [self.sample_values[i] for i in indices]
            else:
                return self.sample_values

    def sampling_str(self, debug: bool) -> str:
        """Generate a string representation of the of the sampling procedure

        Args:
            debug (bool): If true then self.samples_debug is used
        """
        return int_float_sampling_str(self.name, self.values(debug))

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_extra_vars(self)

    def as_dim(self, compute_values=False) -> hv.Dimension:
        return as_dim(self, compute_values=compute_values)


class OptDir(StrEnum):
    minimize = auto()
    maximize = auto()
    none = auto()  # If none this var will not appear in pareto plots


class ResultVar(Number):
    """A class to represent result variables and the desired optimisation direction"""

    __slots__ = ["units", "direction"]

    def __init__(self, units="ul", direction: OptDir = OptDir.minimize, **params):
        Number.__init__(self, **params)
        self.units = units
        self.default = 0  # json is terrible and does not support nan values
        self.direction = direction

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_sha1((self.units, self.direction))


class ResultHmap(param.Parameter):
    """A class to represent a holomap return type"""

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_sha1(self)


class ResultVec(param.List):
    """A class to represent fixed size vector result variable"""

    __slots__ = ["units", "direction", "size"]

    def __init__(self, size, units="ul", direction: OptDir = OptDir.minimize, **params):
        param.List.__init__(self, **params)
        self.units = units
        self.default = 0  # json is terrible and does not support nan values
        self.direction = direction
        self.size = size

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_sha1((self.units, self.direction))

    def index_name(self, idx: int) -> str:
        """given the index of the vector, return the column name that

        Args:
            idx (int): index of the result vector

        Returns:
            str: column name of the vector for the xarray dataset
        """

        mapping = ["x", "y", "z"]
        if idx < 3:
            index = mapping[idx]
        else:
            index = idx
        return f"{self.name}_{index}"

    def index_names(self) -> List[str]:
        """Returns a list of all the xarray column names for the result vector

        Returns:
            list[str]: column names
        """
        return [self.index_name(i) for i in range(self.size)]


class ResultSeries:
    """A class to represent a vector of results, it also includes an index similar to pandas.series"""

    def __init__(self, values=None, index=None) -> None:
        self.values = []
        self.index = []
        self.set_index_and_values(values, index)

    def append(self, value: float | int, index: float | int | str = None) -> None:
        """Add a value and index to the result series

        Args:
            value (float | int): result value of the series
            index (float | int | str, optional): index value of series, the same as a pandas.series index  If no value is passed an integer index is automatically created. Defaults to None.
        """

        if index is None:
            self.index.append(len(self.values))
        else:
            self.index.append(index)
        self.values.append(value)

    def set_index_and_values(
        self, values: List[float | int], index: List[float | int | str] = None
    ) -> None:
        """Add values and indices to the result series

        Args:
            value (List[float | int]): result value of the series
            index (List[float | int | str], optional): index value of series, the same as a pandas.series index  If no value is passed an integer index is automatically created. Defaults to None.
        """
        if values is not None:
            if index is None:
                self.index = list(range(len(values)))
            else:
                self.index = index
            self.values = values


class ResultList(param.Parameter):
    """A class to unknown size vector result variable"""

    __slots__ = ["units", "dim_name", "dim_units", "indices"]

    def __init__(
        self,
        index_name: str,
        index_units: str,
        default=ResultSeries(),
        units="ul",
        indices: List[float] = None,
        instantiate=True,
        **params,
    ):
        param.Parameter.__init__(self, default=default, instantiate=instantiate, **params)
        self.units = units
        self.dim_name = index_name
        self.dim_units = index_units
        self.indices = indices

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_sha1((self.units, self.dim_name, self.dim_units))
