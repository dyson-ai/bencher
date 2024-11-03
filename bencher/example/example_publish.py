"""This file has an example of how to publish a report to github pages"""

import math
import bencher as bch


class SimpleFloat(bch.ParametrizedSweep):
    theta = bch.FloatSweep(
        default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=30
    )
    out_sin = bch.ResultVar(units="v", doc="sin of theta")

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        self.out_sin = math.sin(self.theta)
        return super().__call__(**kwargs)


import functools

if __name__ == "__main__":
    bench = SimpleFloat().to_bench()
    bench.plot_sweep()
    bench.report.publish(functools.partial(bch.publish_github,github_user="blooop",repo_name="reports"),"gh-pages")
