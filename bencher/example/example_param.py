import bencher as bch
import param

class ExampleParam(bch.ParametrizedSweep):

    int_var = param.Integer()

    def __call__(self,**kwargs):



        # self.update_params_from_kwargs(**kwargs)
        return super().__call__()


if __name__ == "__main__":
    bench = ExampleParam().to_bench()

    bench.plot_sweep()
    bench.report.show()
