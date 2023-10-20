from enum import auto
from typing import List

import param
from param import Number
from strenum import StrEnum
import holoviews as hv
from bencher.utils import hash_sha1

# from bencher.variables.parametrised_sweep import ParametrizedSweep


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

    def as_dim(self) -> hv.Dimension:
        return hv.Dimension((self.name, self.name), unit=self.units)

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_sha1((self.units, self.direction))


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


class ResultHmap(param.Parameter):
    """A class to represent a holomap return type"""

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_sha1(self)


def curve(x_vals: List[float], y_vals: List[float], x_name: str, y_name: str, **kwargs) -> hv.Curve:
    return hv.Curve(zip(x_vals, y_vals), kdims=[x_name], vdims=[y_name], label=y_name, **kwargs)


# class ResultCurve(ResultHmap):
#     __slots__ = ["kdim", "vdim", "data"]

#     def __init__(self, kdim, vdim: ResultVar, doc=None, **params) -> None:
#         super().__init__(self, doc=doc, **params)
#         self.kdim = kdim
#         self.vdim = vdim
#         self.data = []

#     def append(self, x, y) -> None:
#         self.data.append((x, y))

#     def to_curve(self, **kwargs) -> hv.Curve:
#         return hv.Curve(
#             self.data,
#             kdims=[self.kdim.as_dim()],
#             vdims=[self.vdim.as_dim()],
#             label=self.vdim.name,
#             **kwargs,
#         )


# class ResultList(param.Parameter):
#     """A class to unknown size vector result variable"""

#     __slots__ = ["units", "dim_name", "dim_units", "indices"]

#     def __init__(
#         self,
#         index_name: str,
#         index_units: str,
#         default=ResultSeries(),
#         units="ul",
#         indices: List[float] = None,
#         instantiate=True,
#         **params,
#     ):
#         param.Parameter.__init__(self, default=default, instantiate=instantiate, **params)
#         self.units = units
#         self.dim_name = index_name
#         self.dim_units = index_units
#         self.indices = indices

#     def hash_persistent(self) -> str:
#         """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
#         return hash_sha1((self.units, self.dim_name, self.dim_units))

# class ResultSeries:
#     """A class to represent a vector of results, it also includes an index similar to pandas.series"""

#     def __init__(self, values=None, index=None) -> None:
#         self.values = []
#         self.index = []
#         self.set_index_and_values(values, index)

#     def append(self, value: float | int, index: float | int | str = None) -> None:
#         """Add a value and index to the result series

#         Args:
#             value (float | int): result value of the series
#             index (float | int | str, optional): index value of series, the same as a pandas.series index  If no value is passed an integer index is automatically created. Defaults to None.
#         """

#         if index is None:
#             self.index.append(len(self.values))
#         else:
#             self.index.append(index)
#         self.values.append(value)

#     def set_index_and_values(
#         self, values: List[float | int], index: List[float | int | str] = None
#     ) -> None:
#         """Add values and indices to the result series

#         Args:
#             value (List[float | int]): result value of the series
#             index (List[float | int | str], optional): index value of series, the same as a pandas.series index  If no value is passed an integer index is automatically created. Defaults to None.
#         """
#         if values is not None:
#             if index is None:
#                 self.index = list(range(len(values)))
#             else:
#                 self.index = index
#             self.values = values
