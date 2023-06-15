import bencher as bch
import numpy as np
from math import sin, cos


class Cfg(bch.ParametrizedSweep):
    offset = bch.FloatSweep(default=0, bounds=[0., 2.], samples=2,units="v")
    # angle = bch.FloatSweep(default=0,bounds=[0,6.28])

    sin_sweep = bch.ResultList(dim_name = "time",dim_units="s",units="v")
    cos_sweep = bch.ResultList(dim_name= "time",dim_units = "s",units="v")


def sin_sweep(offset=0, **kwargs):
    sin_output = []
    cos_output = []
    for i in np.arange(0, 6.28):
        sin_output.append(sin(i)+offset)
    for i in np.arange(0, 3.28):
        cos_output.append(cos(i)+offset)
    return {"sin_sweep": sin_output, "cos_sweep": cos_output}


cfg = Cfg()

bencher = bch.Bench("vector output example", sin_sweep)

bencher.plot_sweep(title="sin", input_vars=[Cfg.param.offset], result_vars=[
                   Cfg.param.sin_sweep, Cfg.param.cos_sweep])

bencher.plot()
