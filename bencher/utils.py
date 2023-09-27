from collections import namedtuple
import xarray as xr
from sortedcontainers import SortedDict
import hashlib
import re
import math
from colorsys import hsv_to_rgb


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


def get_nearest_coords(ds: xr.Dataset, collapse_list=False, **kwargs) -> dict:
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
        if collapse_list and isinstance(cd2[k], list):
            cd2[k] = cd2[k][0]  # select the first item in the list
    return cd2


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


def int_to_col(intVal, sat=0.5, val=0.95):
    golden_ratio_conjugate = (1 + math.sqrt(5)) / 2
    return hsv_to_rgb(intVal * golden_ratio_conjugate, sat, val)
