from enum import Enum
import builtins
from typing import List, Any


import numpy as np
from param import Selector
from bencher.variables.sweep_base import SweepBase, shared_slots


class SweepSelector(Selector, SweepBase):
    """A class to reprsent a parameter sweep of bools"""

    __slots__ = shared_slots

    def __init__(self, units: str = "ul", samples: int = None, **params):
        SweepBase.__init__(self)
        Selector.__init__(self, **params)

        self.units = units
        if samples is None:
            self.samples = len(self.objects)
        else:
            self.samples = samples

    def values(self) -> List[Any]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        return self.indices_to_samples(self.samples, self.objects)


class BoolSweep(SweepSelector):
    """A class to reprsent a parameter sweep of bools"""

    def __init__(self, units: str = "ul", samples: int = None, default=True, **params):
        SweepSelector.__init__(
            self,
            units=units,
            samples=samples,
            default=default,
            objects=[True, False] if default else [False, True],
            **params,
        )


class StringSweep(SweepSelector):
    """A class to reprsent a parameter sweep of strings"""

    def __init__(
        self,
        string_list: List[str],
        units: str = "",
        samples: int = None,
        **params,
    ):
        SweepSelector.__init__(
            self,
            objects=string_list,
            instantiate=True,
            units=units,
            samples=samples,
            **params,
        )


class EnumSweep(SweepSelector):
    """A class to reprsent a parameter sweep of enums"""

    __slots__ = shared_slots

    def __init__(self, enum_type: Enum | List[Enum], units=" ", samples=None, **params):
        # The enum can either be an Enum type or a list of enums
        list_of_enums = isinstance(enum_type, list)
        selector_list = enum_type if list_of_enums else list(enum_type)
        SweepSelector.__init__(
            self,
            objects=selector_list,
            instantiate=True,
            units=units,
            samples=samples,
            **params,
        )
        if not list_of_enums:  # Grab the docs from the enum type def
            self.doc = enum_type.__doc__


class NumberSweep(SweepBase):
    __slots__ = shared_slots + ["units", "samples", "sample_values", "default", "bounds", "step"]

    def __init__(
        self,
        first_arg=None,
        units="ul",
        samples=None,
        sample_values=None,
        default=None,
        bounds=None,
        step=None,
        **params,
    ):
        SweepBase.__init__(self, **params)

        self.units = units
        self.sample_values = sample_values
        self.samples = samples
        self.default = default
        self.bounds = bounds

        self.step = step
        
        self.first_arg_processing(first_arg)

    def first_arg_processing(self, first_arg=None):
        print(type(first_arg))
        if first_arg is not None:
            print(f"using first arg { first_arg}")
            match type(first_arg):
                case builtins.float:
                    self.bounds = (0.0, first_arg)
                    self.default = self.sample_values[0]
                case builtins.int:
                    self.bounds = (0, first_arg)
                    self.default = self.bounds[0]
                    self.step = 1
                case builtins.tuple:
                    print("using tuple bounds")
                    if len(first_arg) == 2:
                        self.bounds = first_arg
                        self.default = self.bounds[0]
                        print(self.default)
                    else:
                        raise RuntimeError(f"tuple bounds must be of length 2 not {len(first_arg)}")
                case builtins.list:
                    self.sample_values = first_arg
                    if self.default is None:
                        self.default = first_arg[0]

        if self.default is None:
            print("setting default")
            if self.sample_values is not None:
                self.default = self.sample_values[0]
            elif self.bounds is not None:
                self.default = self.bounds[0]
            else:
                self.default = 0

        if self.sample_values is None and self.bounds is None:
            raise RuntimeWarning("you must define at least 1 of (bounds,sample_values)")

    def values_base(self, dtype) -> List[float]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        if self.sample_values is None:
            if self.bounds is not None:
                if self.step is None:
                    samps = 2 if self.samples is None else self.samples
                    return np.linspace(self.bounds[0], self.bounds[1], samps, dtype=dtype)
                return np.arange(self.bounds[0], self.bounds[1], self.step, dtype=dtype)
        return self.sample_values


class IntSweep(NumberSweep):
    """A class to reprsent a parameter sweep of ints"""

    __slots__ = shared_slots + ["sample_values", "step"]

    def __init__(
        self,
        first_arg=None,
        default=None,
        units="ul",
        samples=None,
        sample_values=None,
        step=None,
        bounds=None,
        **params,
    ):
        # if first_arg is None:
        # first_arg = [0]

    
        NumberSweep.__init__(
            self,
            first_arg,
            units=units,
            samples=samples,
            sample_values=sample_values,
            default=default,
            step=step,
            bounds=bounds,
            **params,
        )
        if self.sample_values is None:
            if self.step is None:
                self.step = 1

    # def values(self) -> List[int]:
    # """return all the values for a parameter sweep."""
    # return self.values_base(int)

    def values(self) -> List[float]:
        dtype = int
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        if self.sample_values is None:
            if self.bounds is not None:
                if self.step is None:
                    samps = 2 if self.samples is None else self.samples
                    return np.linspace(self.bounds[0], self.bounds[1] + 1, samps, dtype=dtype)
                return np.arange(self.bounds[0], self.bounds[1] + 1, self.step, dtype=dtype)
        return self.sample_values

    # def values(self, dtype) -> List[float]:
    #     """return all the values for a parameter sweep.  If debug is true return a reduced list"""
    #     if self.sample_values is None:
    #         if self.bounds is not None:
    #             if self.step is None:
    #                 samps = 2 if self.samples is None else self.samples
    #                 return np.linspace(self.bounds[0], self.bounds[1], samps, dtype=dtype)
    #             return np.arange(self.bounds[0], self.bounds[1], self.step, dtype=dtype)
    #     return self.sample_values

    # ###THESE ARE COPIES OF INTEGER VALIDATION BUT ALSO ALLOW NUMPY INT TYPES
    # def _validate_value(self, val, allow_None):
    #     if callable(val):
    #         return

    #     if allow_None and val is None:
    #         return

    #     if not isinstance(val, (int, np.integer)):
    #         raise ValueError(
    #             "Integer parameter %r must be an integer, " "not type %r." % (self.name, type(val))
    #         )

    # ###THESE ARE COPIES OF INTEGER VALIDATION BUT ALSO ALLOW NUMPY INT TYPES
    # def _validate_step(self, val, step):
    #     if step is not None and not isinstance(step, (int, np.integer)):
    #         raise ValueError(
    #             "Step can only be None or an " "integer value, not type %r" % type(step)
    #         )


class FloatSweep(NumberSweep):
    """A class to represent a parameter sweep of floats"""

    __slots__ = shared_slots + ["sample_values"]

    def __init__(
        self,
        first_arg=None,
        default=None,
        units="ul",
        samples=None,
        sample_values=None,
        step=None,
        bounds=None,
        **params,
    ):
        # if first_arg is None:
            # first_arg = [0.0]
        NumberSweep.__init__(
            self,
            first_arg,
            units=units,
            samples=samples,
            sample_values=sample_values,
            default=default,
            step=step,
            bounds=bounds,
            **params,
        )

    def values(self) -> List[float]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        return self.values_base(float)


def box(name, center, width):
    var = FloatSweep(default=center, bounds=(center - width, center + width))
    var.name = name
    return var


def with_level(arr: list, level) -> list:
    return IntSweep(sample_values=arr).with_level(level).values()
    # return tmp.with_sample_values(arr).with_level(level).values()
