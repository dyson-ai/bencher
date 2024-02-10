import bencher as bch
import param

# bch.fl


class BenchParameterBase:

    def __init__(self, bounds=None, name=None, level=None, values=None):
        self.name = name
        self.level = level
        self.bounds = None
        self.sample_values = values

    def values(self, level=None):
        pass


class IntSweep(BenchParameterBase):

    def __init__(self, bounds=None, name=None, level=None, values=None):
        super().__init__(bounds, name, level, values)

    def values(self, level=None):

        return super().values(level)


def x_squared(x):
    return x * x


print(x_squared.__annotations__)

args = x_squared.__annotations__

# print(args["x"].doc)

# exit()

bench = bch.Bench(x_squared)

bench.result_vars = bch.result("y")

# api

# bench.sweep(bch.box("x", 0, 1, doc="a real number"))
bench.sweep(bch.float_sweep("x", 0, 10, doc="a real number"))
# bench.sweep(bch.int_sweep("x", 0, 5))
bench.sweep(x=list(range(4)))
bench.sweep(x=range(4))
bench.sweep(x=bch.float_sweep(0, 10, doc="a real number"))


# def x_squared_noise(x,noise):


bench.report.show()
