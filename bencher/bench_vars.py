from enum import Enum, auto
from strenum import StrEnum

import numpy as np
import param
from pandas import Timestamp
import re
from datetime import datetime
from typing import List


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

    return capitalise_words(
        re.sub("([a-z])([A-Z])", r"\g<1> \g<2>", camel.replace("_", " "))
    )


def param_hash(
    param_type: param.Parameterized, hash_value: bool = True, hash_meta: bool = False
) -> int:
    """A custom hash function for parametrised types with options for hashing the value of the type and hashing metadata

    Args:
        param_type (param.Parameterized): A parameter
        hash_value (bool, optional): use the value as part of the hash. Defaults to True.
        hash_meta (bool, optional): use metadata as part of the hash. Defaults to False.

    Returns:
        int: a hash
    """

    curhash = 0
    if hash_value:
        for k, v in param_type.param.values().items():
            if k != "name":
                curhash = hash((curhash, hash(v)))

    if hash_meta:
        for k, v in param_type.param.params().items():
            if k != "name":
                print(f"key:{k}, hash:{hash(k)}")
                print(f"value:{v}, hash:{hash(v)}")
                curhash = hash((curhash, hash(k), hash(v)))
    return curhash


class ParametrizedSweep(param.Parameterized):
    """Parent class for all Sweep types that need a custom hash"""

    def __hash__(self) -> int:
        return param_hash(self, True, False)


class ParametrizedOutput(param.Parameterized):
    """Parent class for all Output types that need a custom hash"""

    def __hash__(self) -> int:
        return param_hash(self, True, False)


# slots that are shared across all Sweep classes
# param does not work with multiple inheritance so define here
shared_slots = ["units", "samples", "samples_debug"]


def sweep_hash(parameter: param.Parameterized) -> int:
    """Generate a hash for a sweep variable

    Returns:
        int: hash
    """
    curhash = 0
    for v in parameter.values():
        print(f"value:{v}, hash:{hash(v)}")
        curhash = hash((curhash, hash(v)))
    return curhash


def hash_extra_vars(parameter: param.Parameterized) -> int:
    """hash extra meta vars in the parameter

    Args:
        parameter (param.Parameterized): a parameter

    Returns:
        int: hash
    """
    return hash((parameter.units, parameter.samples, parameter.samples_debug))


def describe_variable(
    v: param.Parameterized, debug: bool, include_samples: bool, indent_count=1
) -> List[str]:
    """Generate a string description of a variable

    Args:
        v (param.param.Parameterized): parameter to describe
        debug (bool): Generate a reduced param.Number of samples from the variable
        include_samples (bool): Include a description of the samples
        indent_count (int, optional): param.Number of times to indent the string. Defaults to 1.

    Returns:
        str: String description of the variable
    """
    indent = "    "
    indent *= indent_count
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


class BoolSweep(param.Boolean):
    """A class to represent a parameter sweep of bools"""

    __slots__ = shared_slots

    def __init__(
        self, units: str = "ul", samples: int = None, samples_debug: int = 2, **params
    ):
        param.Boolean.__init__(self, **params)
        self.units = units
        if samples is None:
            self.samples = 2
        self.samples_debug = samples_debug

    def values(self, debug) -> list[bool]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        print(self.sampling_str(debug))
        return [True, False]

    def sampling_str(self, debug: bool) -> str:
        """Generate a string representation of the sampling procedure"""
        print(self.sampling_str(debug))
        return f"sampling {self.name} from: [True,False]"

    def __hash__(self) -> int:
        return hash_extra_vars(self)


class TimeBase(param.Selector):
    """A class to capture a time snapshot of benchmark values.  Time is reprented as a continous value i.e a datetime which is converted into a np.datetime64.  To represent time as a discrete value use the TimeEvent class. The distinction is because holoview and plotly code makes different assumptions about discrete vs continous variables"""

    __slots__ = shared_slots

    def values(self, debug) -> List[str]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        print(self.sampling_str(debug))
        return self.objects

    def sampling_str(self, debug: bool) -> str:
        """Generate a string representation of the time sample

        Args:
            debug (bool): If true then self.samples_debug is used
        """
        print(self.sampling_str(debug))
        return f"sampling from [The Past to {self.objects[0]}]"

    def __hash__(self) -> int:
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
        super().__init__()
        if type(datetime_src) == str:
            param.Selector.__init__(self, [datetime_src], instantiate=True, **params)
        else:
            param.Selector.__init__(
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
    """A class to represent a discrete event in time where the data was captured i.e a series of pull requests.  Here time is discrete and can't be interpolated, to represent time as a continous value use the TimeSnapshot class.  The distinction is because holoview and plotly code make different assumptions about discrete vs continous variables"""

    __slots__ = shared_slots

    def __init__(
        self,
        time_event: str,
        units: str = "event",
        samples: int = None,
        samples_debug: int = 2,
        **params,
    ): 
        super().__init__()
        param.Selector.__init__(
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


class StringSweep(param.Selector):
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
        param.Selector.__init__(self, string_list, instantiate=True, **params)
        self.units = units
        if samples is None:
            self.samples = len(self.objects)
        else:
            self.samples = samples
        self.samples_debug = min(self.samples, samples_debug)

    def values(self, debug) -> List[str]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        print(self.sampling_str(debug))
        return self.objects

    def sampling_str(self, debug: bool) -> str:
        """Generate a string representation of the of the sampling procedure

        Args:
            debug (bool): If true then self.samples_debug is used
        """
        object_str = ",".join([i for i in self.objects])
        print(self.sampling_str(debug))
        return f"sampling {self.name} from: [{object_str}]"

    def __hash__(self) -> int:
        return hash_extra_vars(self)


class EnumSweep(param.Selector):
    """A class to reprsent a parameter sweep of enums"""

    __slots__ = shared_slots

    def __init__(
        self,
        enum_type: Enum | List[Enum],
        units="ul",
        samples=None,
        samples_debug=2,
        **params,
    ):
        # The enum can either be an Enum type or a list of enums
        list_of_enums = type(enum_type) is list
        if list_of_enums:
            param.Selector_list = enum_type  # already a list of enums
        else:
            # create a list of enums from the enum type definition
            param.Selector_list = [e for e in enum_type]
        param.Selector.__init__(self, param.Selector_list, **params)
        if not list_of_enums:  # Grab the docs from the enum type def
            self.doc = enum_type.__doc__
        self.units = units
        if samples is None:
            self.samples = len(self.objects)
        else:
            self.samples = samples
        self.samples_debug = min(self.samples, samples_debug)

    def values(self, debug) -> List[Enum]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        print(self.sampling_str(debug))
        return self.objects

    def sampling_str(self, debug: bool) -> str:
        """Generate a string representation of the of the sampling procedure

        Args:
            debug (bool): If true then self.samples_debug is used
        """
        object_str = ",".join([i for i in self.objects])
        print(self.sampling_str(debug))
        return f"sampling {self.name} from: [{object_str}]"

    def __hash__(self) -> int:
        return hash_extra_vars(self)


def int_float_sampling_str(name, samples) -> str:
    """Generate a string representation of the of the sampling procedure

    Args:
        debug (bool): If true then self.samples_debug is used
    """

    return f"sampling {name} from {samples} in {len(samples)} samples"


class IntSweep(param.Integer):
    """A class to represent a parameter sweep of ints"""

    __slots__ = shared_slots + ["sample_values"]

    def __init__(
        self, units="ul", samples=None, samples_debug=2, sample_values=None, **params
    ):
        param.Integer.__init__(self, **params)
        self.units = units
        self.samples_debug = samples_debug

        if sample_values is None:
            if samples is None:
                if self.bounds is None:
                    raise RuntimeError("You must define bounds for param.Integer types")
                else:
                    self.samples = self.bounds[1] - self.bounds[0]
            else:
                self.samples = samples
            self.sample_values = None
        else:
            self.sample_values = sample_values
            self.samples = len(self.sample_values)
            if not "default" in params:
                self.default = sample_values[0]

    def values(self, debug) -> List[int]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        samps = self.samples_debug if debug else self.samples

        if self.sample_values is None:
            return [
                int(i)
                for i in np.linspace(self.bounds[0], self.bounds[1], samps, dtype=int)
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

    def __hash__(self) -> int:
        return hash_extra_vars(self)


class FloatSweep(param.Number):
    """A class to represent a parameter sweep of floats"""

    __slots__ = shared_slots + ["sample_values"]

    def __init__(
        self, units="ul", samples=10, samples_debug=2, sample_values=None, **params
    ):
        param.Number.__init__(self, **params)
        self.units = units
        self.samples_debug = samples_debug
        if sample_values is None:
            self.samples = samples
            self.sample_values = None
        else:
            self.sample_values = sample_values
            self.samples = len(self.sample_values)
            if not "default" in params:
                self.default = sample_values[0]

    def values(self, debug) -> List[float]:
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

    def __hash__(self) -> int:
        return hash_extra_vars(self)


class OptDir(StrEnum):
    minimize = auto()
    maximize = auto()
    none = auto()  # If none this var will not appear in pareto plots


class ResultVar(param.Number):
    """A class to represent result variables and the desired optimisation direction"""

    __slots__ = ["units", "direction"]

    def __init__(self, units="ul", direction: OptDir = OptDir.minimize, **params):
        param.Number.__init__(self, **params)
        self.units = units
        self.default = 0  # json is terrible and does not support nan values
        self.direction = direction

    def __hash__(self) -> int:
        return hash((self.units, self.direction))


class ResultVec(param.List):
    """A class to represent vector result variable"""

    __slots__ = ["units", "direction", "size"]

    def __init__(self, size, units="ul", direction: OptDir = OptDir.minimize, **params):
        param.List.__init__(self, **params)
        self.units = units
        self.default = 0  # json is terrible and does not support nan values
        self.direction = direction
        self.size = size

    def __hash__(self) -> int:
        return hash((self.units, self.direction))

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

    def index_names(self) -> list[str]:
        """Returns a list of all the xarray column names for the result vector

        Returns:
            list[str]: column names
        """
        return [self.index_name(i) for i in range(self.size)]
