import bencher as bch
import random
from bokeh.io import output_notebook

class SimpleFloat0D(bch.ParametrizedSweep):
    """This class has 0 input dimensions and 1 output dimensions.  It samples from a gaussian distribution"""

    # This defines a variable that we want to plot
    output = bch.ResultVar(units="ul", doc="a sample from a gaussian distribution")

    def __call__(self, **kwargs) -> dict: 
        return dict(output=random.gauss(mu=0.0, sigma=1.0))
        


bench = SimpleFloat0D().to_bench(bch.BenchRunCfg(repeats=100)
)
res=bench.plot_sweep()

