# pylint: disable=duplicate-code


import bencher as bch
import holoviews as hv

class InteractiveExplorer(bch.ParametrizedSweep):

    ###INPUTS
    theta = FloatSweep(default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=30)
    offset = FloatSweep(default=0, bounds=[0, 0.3], doc="dc offset", units="v", samples=30)
    noisy = BoolSweep(
        default=False, doc="Optionally add random noise to the output of the function"
    )

    noise_distribution = EnumSweep(NoiseDistribution, doc=NoiseDistribution.__doc__)

    sigma = FloatSweep(
        default=1,
        bounds=[0, 10],
        doc="The standard deviation of the noise",
        units="v",
    )

    #RESULTS

    out_sin = ResultVar(units="v", direction=OptDir.minimize, doc="sin of theta with some noise")
    out_cos = ResultVar(units="v", direction=OptDir.minimize, doc="cos of theta with some noise")

    def __call__(self,**kwargs):
        self.update_from_kwargs(**kwargs)

        out_sin = postprocess_fn(cfg.offset + math.sin(cfg.theta) + noise)
        out_cos = postprocess_fn(cfg.offset + math.cos(cfg.theta) + noise)

        return self.get_results_values_as_dict()

    def plot(self):
        origin = [0,0]
        res = [out_sin,out_cos]
        points = [origin,res]
        return hv.Points(points)*        hv.Curve(points)





def bench_function(**kwargs) -> dict:
    """Takes an ExampleBenchCfgIn and returns a ExampleBenchCfgOut output"""
    out = ExampleBenchCfgOut()
    noise = calculate_noise(cfg)


    out.out_sin = postprocess_fn(offset + math.sin(cfg.theta) + noise)
    out.out_cos = postprocess_fn(offset + math.cos(cfg.theta) + noise)

    out.out_bool = out.out_sin > 0.5
    return out






if __name__ == "__main__":
    ex_run_cfg = BenchRunCfg(repeats=10)

    example_floats(ex_run_cfg).plot()
