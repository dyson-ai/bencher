from enum import Enum
from typing import List, Any

import numpy as np
from dataclasses import dataclass
from typing import Tuple
from abc import abstractmethod

# class SweepSelector(Selector, SweepBase):
#     """A class to reprsent a parameter sweep of bools"""

#     __slots__ = shared_slots

#     def __init__(self, units: str = "ul", samples: int = None, samples_debug: int = 2, **params):
#         SweepBase.__init__(self)
#         Selector.__init__(self, **params)

#         self.units = units
#         if samples is None:
#             self.samples = len(self.objects)
#         else:
#             self.samples = samples
#         self.samples_debug = min(self.samples, samples_debug)

#     def values(self, debug=False) -> List[Any]:
#         """return all the values for a parameter sweep.  If debug is true return a reduced list"""
#         return self.indices_to_samples(self.samples_debug if debug else self.samples, self.objects)


# class BoolSweep(SweepSelector):
#     """A class to reprsent a parameter sweep of bools"""

#     def __init__(
#         self, units: str = "ul", samples: int = None, samples_debug: int = 2, default=True, **params
#     ):
#         SweepSelector.__init__(
#             self,
#             units=units,
#             samples=samples,
#             samples_debug=samples_debug,
#             default=default,
#             objects=[True, False] if default else [False, True],
#             **params,
#         )


# class StringSweep(SweepSelector):
#     """A class to reprsent a parameter sweep of strings"""

#     def __init__(
#         self,
#         string_list: List[str],
#         units: str = "",
#         samples: int = None,
#         samples_debug: int = 2,
#         **params,
#     ):
#         SweepSelector.__init__(
#             self,
#             objects=string_list,
#             instantiate=True,
#             units=units,
#             samples=samples,
#             samples_debug=samples_debug,
#             **params,
#         )


# class EnumSweep(SweepSelector):
#     """A class to reprsent a parameter sweep of enums"""

#     __slots__ = shared_slots

#     def __init__(
#         self, enum_type: Enum | List[Enum], units=" ", samples=None, samples_debug=2, **params
#     ):
#         # The enum can either be an Enum type or a list of enums
#         list_of_enums = isinstance(enum_type, list)
#         selector_list = enum_type if list_of_enums else list(enum_type)
#         SweepSelector.__init__(
#             self,
#             objects=selector_list,
#             instantiate=True,
#             units=units,
#             samples=samples,
#             samples_debug=samples_debug,
#             **params,
#         )
#         if not list_of_enums:  # Grab the docs from the enum type def
#             self.doc = enum_type.__doc__


#     def values(self, debug=False) -> List[int]:
#         """return all the values for a parameter sweep.  If debug is true return the  list"""
#         sample_values = (
#             self.sample_values
#             if self.sample_values is not None
#             else list(range(int(self.bounds[0]), int(self.bounds[1] + 1)))
#         )

#         return self.indices_to_samples(self.samples_debug if debug else self.samples, sample_values)


def with_level(items: list, level=None):
    if level is None:
        return items
    level_sample_map = [0, 1, 2, 3, 5, 9, 17, 33, 65, 129, 257, 513, 1025, 2049]
    return indices_to_samples(level_sample_map[level], items)


def indices_to_samples(desires_num_samples, sample_values):
    indices = [
        int(i) for i in np.linspace(0, len(sample_values) - 1, desires_num_samples, dtype=int)
    ]

    if len(indices) > len(sample_values):
        return sample_values

    return [sample_values[i] for i in indices]


@dataclass
class BenchParameterBase:

    values: List = None
    bounds: Tuple = None
    name: str = None
    samples: int = None
    step: int = None
    default: Any = None
    units: str = None
    level: int = None

    def get_values(self, level=None, samples=None):
        if level is None:
            level = self.level
        if samples is None:
            samples = self.samples
        if samples is not None:
            return indices_to_samples(samples, self.get_sample_values())
        if level is not None:
            return with_level(self.get_sample_values(), level)
        return self.get_sample_values()

    @abstractmethod
    def get_sample_values(self):
        pass

    def get_default(self):
        if self.default is not None:
            return self.default
        
        if self.bounds is not None:
            return self.bounds[0]
        
        return self.get_sample_values()[0]

    # def default(self):

    # if self.sample_values is not None:
    # return self.sample_values
    # if self.bounds is not None:
    # return


# def int_sweep(values=None):
# if values is None:
# BenchParameterBase()

# if isinstance(var1,str):

# for arg in args:
# match type(args):
# case int:


class IntSweep(BenchParameterBase):

    # def __post_init__(self):
        # if isinstance(self.values,int):
            # self.values = [self.values]

        # print("here")
        # exit()
        # match type(self.values):
            # case int:
                # self.values = [self.values]
            # case list:
            # pass
        # if self.values

    def get_sample_values(self) -> List[int]:
        if self.values is not None:
            if isinstance(self.values,int):
                return [self.values]
            return self.values
        if self.bounds is not None:
            return list(range(int(self.bounds[0]), int(self.bounds[1] + 1)))
        return [0]

  





class FloatSweep(BenchParameterBase):
    """A class to represent a parameter sweep of floats"""

    def get_sample_values(self):
        if self.values is not None:
            return self.values
        if self.bounds is not None:
            return np.arange(self.bounds[0], self.bounds[1], self.step)

    def get_default(self):
        return 0 if self.default is None else self.default


class CatSweep(BenchParameterBase):
    def get_sample_values(self):
        if self.values is not None:
            if isinstance(self.values, Enum):
                return list(self.values)
            return self.values
        return []


def box(name, center, width, doc=None):
    var = FloatSweep(default=center, bounds=(center - width, center + width))
    var.name = name
    var.doc = doc
    return var


def float_sweep(name, min_val, max_val, doc=None):
    var = FloatSweep(bounds=(min_val, max_val))
    var.name = name
    var.doc = doc
    return var


def int_sweep(name, min_val, max_val):
    var = FloatSweep(bounds=(min_val, max_val))
    var.name = name


# if __name__ == "__main__":
    