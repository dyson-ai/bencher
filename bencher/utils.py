from collections import namedtuple
import xarray as xr
from sortedcontainers import SortedDict
import hashlib
import re
import math
from colorsys import hsv_to_rgb
from pathlib import Path
from uuid import uuid4
from functools import partial
from typing import Callable, Any, List, Tuple
import param
import numpy as np


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


def get_nearest_coords(dataset: xr.Dataset, collapse_list=False, **kwargs) -> dict:
    """Given an xarray dataset and kwargs of key value pairs of coordinate values, return a dictionary of the nearest coordinate name value pair that was found in the dataset

    Args:
        ds (xr.Dataset): dataset

    Returns:
        dict: nearest coordinate name value pair that matches the input coordinate name value pairs.
    """

    selection = dataset.sel(method="nearest", **kwargs)
    cd = selection.coords.to_dataset().to_dict()["coords"]
    cd2 = {}
    for k, v in cd.items():
        cd2[k] = v["data"]
        if collapse_list and isinstance(cd2[k], list):
            cd2[k] = cd2[k][0]  # select the first item in the list
    return cd2


def get_nearest_coords1D(val: Any, coords) -> Any:
    if isinstance(val, (int, float)):
        return min(coords, key=lambda x_: abs(x_ - val))
    for i in coords:
        if val == i:
            return i
    return val


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


def mult_tuple(inp: Tuple[float], val: float) -> Tuple[float]:
    return tuple(np.array(inp) * val)


def tabs_in_markdown(regular_str: str, spaces: int = 2) -> str:
    """Given a string with tabs in the form \t convert the to &ensp; which is a double space in markdown

    Args:
        regular_str (str): A string with tabs in it
        spaces (int): the number of spaces per tab

    Returns:
        str: A string with sets of &nbsp; to represent the tabs in markdown
    """
    return regular_str.replace("\t", "".join(["&nbsp;"] * spaces))


def int_to_col(int_val, sat=0.5, val=0.95, alpha=-1) -> tuple[float, float, float]:
    """Uses the golden angle to generate colors programmatically with minimum overlap between colors.
    https://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/

    Args:
        int_val (_type_): index of an object you want to color, this is mapped to hue in HSV
        sat (float, optional): saturation in HSV. Defaults to 0.5.
        val (float, optional): value in HSV. Defaults to 0.95.
        alpha (int, optional): transparency.  If -1 then only RGB is returned, if 0 or greater, RGBA is returned. Defaults to -1.

    Returns:
        tuple[float, float, float] | tuple[float, float, float, float]: either RGB or RGBA vector
    """
    golden_ratio_conjugate = (1 + math.sqrt(5)) / 2
    rgb = hsv_to_rgb(int_val * golden_ratio_conjugate, sat, val)
    if alpha >= 0:
        return (*rgb, alpha)
    return rgb


def lerp(value, input_low: float, input_high: float, output_low: float, output_high: float):
    input_low = float(input_low)
    return output_low + ((float(value) - input_low) / (float(input_high) - input_low)) * (
        float(output_high) - output_low
    )


def color_tuple_to_css(color: tuple[float, float, float]) -> str:
    return f"rgb{(color[0] * 255, color[1] * 255, color[2] * 255)}"


def color_tuple_to_255(color: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        min(int(color[0] * 255), 255),
        min(int(color[1] * 255), 255),
        min(int(color[2] * 255), 255),
    )


def gen_path(filename, folder="generic", suffix=".dat"):
    path = Path(f"cachedir/{folder}/{filename}/")
    path.mkdir(parents=True, exist_ok=True)
    return f"{path.absolute().as_posix()}/{filename}_{uuid4()}{suffix}"


def gen_video_path(video_name: str = "vid", extension: str = ".mp4") -> str:
    return gen_path(video_name, "vid", extension)


def gen_image_path(image_name: str = "img", filetype=".png") -> str:
    return gen_path(image_name, "img", filetype)


def callable_name(any_callable: Callable[..., Any]) -> str:
    if isinstance(any_callable, partial):
        return any_callable.func.__name__
    try:
        return any_callable.__name__
    except AttributeError:
        return str(any_callable)


def listify(obj) -> list:
    """Take an object and turn it into a list if its not already a list.  However if the object is none, don't turn it into a list"""
    if obj is None:
        return None
    if isinstance(obj, list):
        return obj
    if isinstance(obj, tuple):
        return list(obj)
    return [obj]


def get_name(var):
    if isinstance(var, param.Parameter):
        return var.name
    return var


def params_to_str(param_list: List[param.Parameter]):
    return [get_name(i) for i in param_list]
