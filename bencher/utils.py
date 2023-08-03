from collections import namedtuple
import xarray as xr
from sortedcontainers import SortedDict


def hmap_canonical_input(dic: dict) -> tuple:
    """From a dictionary of kwargs, return a hashable representation (tuple) that is always the same for the same inputs and retains the order of the input arguments.  e.g, {x=1,y=2} -> (1,2) and {y=2,x=1} -> (1,2).  This is used so that keywords arguments can be hashed and converted the the tuple keys that are used for holomaps

    Args:
        dic (dict): dictionary with keyword arguments and values in any order

    Returns:
        tuple: values of the dictionary always in the same order and hashable
    """

    function_input = SortedDict(dic)
    return tuple(function_input.values())


def make_namedtuple(class_name: str, **fields) -> namedtuple:
    """Convenience method for making a named tuple

    Args:
        class_name (str): name of the named tuple

    Returns:
        namedtuple: a named tuple with the fields as values
    """
    return namedtuple(class_name, fields)(*fields.values())


def get_nearest_coords(ds: xr.Dataset, **kwargs) -> dict:
    """Given an xarray dataset and kwargs of key value pairs of coordinate values, return a dictionary of the nearest coordinate name value pair that was found in the dataset

    Args:
        ds (xr.Dataset): dataset

    Returns:
        dict: nearest coordinate name value pair that matches the input coordinate name value pairs.
    """

    selection = ds.sel(method="nearest", **kwargs)
    cd = selection.coords.to_dataset().to_dict()["coords"]
    cd2 = {}
    for k, v in cd.items():
        cd2[k] = v["data"]
    return cd2
