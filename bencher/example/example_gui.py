# THIS IS NOT A WORKING EXAMPLE YET

# pylint: disable=duplicate-code,unused-argument


import bencher as bch
import math
import random
import numpy as np
import holoviews as hv

from strenum import StrEnum
from enum import auto


class Function(StrEnum):
    fn_cos = auto()
    fn_sin = auto()
    fn_log = auto()
    fn_arctan = auto()

    def call(self, arg) -> float:
        """Calls the function defined by the name of the enum

        Returns:
            float: The result of calling the function defined by the enum
        """
        return getattr(np, self.removeprefix("fn_"))(arg)


class PlotFunctions(bch.ParametrizedSweep):
    phase = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=5
    )

    freq = bch.FloatSweep(default=1, bounds=[0, math.pi], doc="Input angle", units="rad", samples=5)

    # theta = bch.FloatSweep(
    #     default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=10
    # )

    # compute_fn = bch.EnumSweep(Function)

    # fn_output = bch.ResultVar(units="v", doc="sin of theta with some noise")

    # out_sum = bch.ResultVar(units="v", doc="The sum")

    hmap = bch.ResultHmap()

    def __call__(self, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)
        # noise = 0.1

        # self.fn_output = self.compute_fn.call(self.phase + self.freq * self.theta) + random.uniform(
        #     0, noise
        # )
        print(kwargs)

        self.hmap = self.plot_holo(True)
        return super().__call__()

    def plot_holo(self, plot=True) -> hv.core.ViewableElement:
        """Plots a generic representation of the object that is not a basic hv datatype. In this case its an image of the values of the object, but it could be any representation of the object, e.g. a screenshot of the object state"""
        # pt = hv.Text(0, 0, f"{self.phase}\n{self.freq}\n {self.theta}")
        pt = hv.Text(0, 0, f"{self.phase}\n{self.freq}")

        pt *= hv.Ellipse(0, 0, 1)
        return pt


import panel as pn
from functools import partial


def example_gui():

    pf = PlotFunctions()

    pf.to_gui()

    def sine_curve(phase, freq):
        xvals = [0.1 * i for i in range(100)]
        return hv.Curve((xvals, [np.sin(phase + freq * x) for x in xvals]))

    def callback_wrapper(**kwargs):
        return pf.__call__(**kwargs)["hmap"]

    # pn.Row(pf.__call__()).show()

    # dmap = pf.to_dynamic_map()

    # When run live, this cell's output should match the behavior of the GIF below
    # dmap = hv.DynamicMap(pf.__call__, kdims=["phase", "freq"])
    # dmap = hv.DynamicMap(callback_wrapper, kdims=["phase", "freq"])

    # dmap = hv.DynamicMap(
    #     callback_wrapper,
    #     kdims=[hv.Dimension("phase", range=(0.5, 1)), hv.Dimension("freq", range=(0.5, 1.25))],
    # )

    # dmap = hv.DynamicMap(sine_curve, kdims=["phase", "freq"])

    # dmap = dmap.redim.range(phase=(0.5, 1), freq=(0.5, 1.25))

    # pn.Row(dmap).show()


if __name__ == "__main__":
    example_gui()
