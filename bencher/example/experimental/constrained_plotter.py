from __future__ import annotations
from typing import List, Tuple
import bencher as bch
import numpy as np
import holoviews as hv
from numpy.random import uniform
from dataclasses import dataclass
from copy import deepcopy
import math
import yaml


@dataclass
class Point:

    x: float = 0
    y: float = 0

    def delta(self, x: float = 0.0, y: float = 0.0, clamp_int=False) -> Point:
        """add delta to the current x and y points and mutates it

        Args:
            x (float, optional): time. Defaults to 0.
            y (float, optional): oxygen. Defaults to 0.
            clamp_int (bool, optional): if set to true it will set x and y to the nearest int. Defaults to False.

        Returns:
            Point: mutated point with delta added
        """
        self.x += x
        self.y += y
        if clamp_int:
            self.y = round(self.y, 0)
            self.x = round(self.x, 0)

        return self

    def __add__(self, p: Point) -> Point:
        """dunder method for adding"""
        return self.delta(p.x, p.y)

    def gradient(self, prev_point: Point) -> float:
        """Calulate the gradient between the current point and another point

        Args:
            prev_point (Point): any point

        Returns:
            float: gradient
        """
        x_delta = prev_point.x - self.x
        y_delta = prev_point.y - self.y
        grad = y_delta / x_delta
        return grad

    def deep(self) -> Point:
        """returns a deep copy of the point

        Returns:
            Point: deep copy
        """
        return deepcopy(self)

    def as_tuple(self) -> Tuple[2]:
        return (self.x, self.y)

    def as_dict(self) -> dict:
        return {"x": self.x, "y": self.y}


class Stylus:

    def __init__(self, point: Point = None) -> None:
        """Initialises the styllus to a point and adds that point to the graph

        Args:
            point (Point, optional): Defaults to 0,0.
        """
        self.p = Point() if point is None else point
        self.points = []
        self.add()

    def delta(self, x: float = 0.0, y: float = 0.0, clamp_int: bool = False) -> Stylus:
        """Modifies the existing point with a delta and adds it to the graph

        Args:
            x (float, optional): delta for x. Defaults to 0.
            y (float, optional): delta for y. Defaults to 0.
            clamp_int (bool, optional): _description_. Defaults to False.

        Returns:
            Stylus: the stylus moved by delta
        """
        self.p.delta(x=x, y=y, clamp_int=clamp_int)
        return self.add()

    def add(self):
        """Adds the current stylus position to the graph"""
        self.points.append(self.p.deep())
        return self

    def add_abs_point(self, x: float = None, y: float = None):
        self.p.x = self.p.x if x is None else x
        self.p.y = self.p.y if y is None else y
        return self.add()

    def add_pt_with_grad(
        self,
        x_delta: float = 0.0,
        gradient: float = 0.0,
        x_delta_range: float = 0.0,
        gradient_range: float = 0.0,
        clamp_int: bool = False,
    ) -> Stylus:
        """takes the current point and generates a new point with specified gradient and optional ranges

        Args:
            x_delta (float, optional): delta in x between the current point and the newly created point. Defaults to 0.
            gradient (float, optional): the gradient between the current point and the added point. Defaults to 0.
            x_delta_range (float, optional): plus minus value for the delta x. Defaults to 0.
            gradient_range (float, optional): plus minus value for the gradient. Defaults to 0.
            clamp_int (bool, optional): Defaults to False.

        Returns:
            Stylus: returns the modified stylus
        """
        self.delta(
            x_delta + uniform(-x_delta_range, x_delta_range),
            uniform(gradient - gradient_range, gradient + gradient_range) * x_delta,
            clamp_int=clamp_int,
        )
        return self

    def add_pt_y_diff_with_grad(
        self,
        y_delta: float = 0.0,
        gradient: float = 0.0,
        y_delta_range: float = 0.0,
        gradient_range: float = 0.0,
        clamp_int: bool = False,
    ) -> Stylus:
        """takes the current point and generates a new point with specified gradient and optional ranges

        Args:
            x_delta (float, optional): delta in x between the current point and the newly created point. Defaults to 0.
            gradient (float, optional): the gradient between the current point and the added point. Defaults to 0.
            x_delta_range (float, optional): plus minus value for the delta x. Defaults to 0.
            gradient_range (float, optional): plus minus value for the gradient. Defaults to 0.
            clamp_int (bool, optional): Defaults to False.

        Returns:
            Stylus: returns the modified stylus
        """
        y_delta += uniform(-y_delta_range, y_delta_range)
        gradient += uniform(-gradient_range, gradient_range)
        x_delta = y_delta / gradient
        return self.delta(x_delta, y_delta, clamp_int=clamp_int)

    def add_pt_with_grad_ratio(
        self,
        x_delta: float = 0.0,
        gradient_ratio: float = 0.0,
        gradient_ratio_range: float = 0.0,
    ) -> Stylus:
        """takes the current point and generates a new point with specified gradient and optional ranges

        Args:
            x_delta (float, optional): delta in x between the current point and the newly created point. Defaults to 0.
            gradient_ratio (float, optional): the gradient ratio between the current point and the added point. Defaults to 0.
            gradient_ratio_range (float, optional): plus minus value for the gradient ratio. Defaults to 0.

        Returns:
            Stylus: returns the modified stylus
        """
        x_delta = float(x_delta)
        gradient_ratio = float(gradient_ratio)
        gradient_ratio_range = float(gradient_ratio_range)

        prev_gradient = self.p.gradient(self.points[-2])
        gradient_ratio += uniform(-gradient_ratio_range, gradient_ratio_range)
        next_gradient = prev_gradient / gradient_ratio

        self.add_pt_with_grad(
            x_delta=x_delta,
            gradient=next_gradient,
        )
        return self

    def to_tuples(self) -> List[Tuple[2]]:
        out = []
        for p in self.points:
            out.append(p.as_tuple())
        return out

    def to_dict(self) -> dict:
        out = {}
        for i, p in enumerate(self.points):
            out[str(i + 1)] = p.as_dict()
        return out

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict)

    def to_curve(self, valid: bool = None) -> hv.Curve:
        """converts the points into a holoview curve

        Args:
            valid (bool, optional): if valid is true the curve is green, else red. Defaults to None.

        Returns:
            hv.Curve: points as a curve
        """
        if valid is not None:
            return hv.Curve(
                self.to_tuples(),
            ).opts(color="green" if valid else "red")
        return hv.Curve(self.to_tuples())

    def to_labels(self, round_digits=None) -> hv.Labels:
        """takes all the points and adds x,y label strings for all the points

        Args:
            round_digits (_type_, optional): rounds x,y coordinates to a specified number of decimal points. Defaults to None.

        Returns:
            hv.Labels: x,y labels
        """
        data = self.to_tuples()
        if round_digits is not None:
            label_vals = [f"{d[0],d[1]}" for d in data]
        else:
            label_vals = [f"{round(d[0],round_digits),round(d[1],round_digits)}" for d in data]

        return hv.Labels({("x", "y"): data, "text": label_vals}, ["x", "y"], "text")


# https://param.holoviz.org/user_guide/Dynamic_Parameters.html
