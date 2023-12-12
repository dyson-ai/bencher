import numpy as np
import panel as pn
import xarray as xr


# data = np.random.rand(2, 3, 4)

# for i,x in enumerate(range(1,2)):
#     for j,y in enumerate(range(2,3)):
#         for k,z in enumerate(range(3,4)):
#             # data[i,j,k] = x

#     for j in range(2,3):
#         for k in range(4,5):
#             data[i,j,k]


# coords = {
#     "x": np.linspace(0, 1, 2),
#     "y": np.linspace(10, 20, 3),
#     "z": np.linspace(100, 110, 4),
# }
# da3 = xr.DataArray(data, coords=coords, dims=["x", "y", "z"])

import bencher as bch


class TestPrinting(bch.ParametrizedSweep):
    # INPUTS
    a = bch.StringSweep(default=None, string_list=["a1", "a2"], allow_None=True)
    b = bch.StringSweep(default=None, string_list=["b1", "b2"], allow_None=True)
    c = bch.StringSweep(default=None, string_list=["c1", "c2"], allow_None=True)
    d = bch.StringSweep(default=None, string_list=["d1", "d2"], allow_None=True)

    # RESULTS
    result = bch.ResultString()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)

        self.result = self.a
        if self.b is not None:
            self.result += f",{self.b}"
        if self.c is not None:
            self.result += f",{self.c}"
        if self.d is not None:
            self.result += f",{self.d}"
        return super().__call__()


run_cfg = bch.BenchRunCfg()
run_cfg.auto_plot = False

bench = bch.Bench("tp", TestPrinting(), run_cfg=run_cfg)

for s in [
    [TestPrinting.param.a],
    [TestPrinting.param.a, TestPrinting.param.b],
    [TestPrinting.param.a, TestPrinting.param.b, TestPrinting.param.c],
    [TestPrinting.param.a, TestPrinting.param.b, TestPrinting.param.c, TestPrinting.param.d],

]:
    res1 = bench.plot_sweep("t1", input_vars=s)
    resA = bch.PanelResult(res1.ds, res1)
    bench.report.append_tab(resA.to_panes())


# res1 = bench.plot_sweep("t1", input_vars=[TestPrinting.param.a])
# res2 = bench.plot_sweep("t2", input_vars=[TestPrinting.param.a, TestPrinting.param.b])
# res3 = bench.plot_sweep(
#     "t3", input_vars=[TestPrinting.param.a, TestPrinting.param.b, TestPrinting.param.c]
# )


# resA = bch.PanelResult(res1.ds, res1)
# resB = bch.PanelResult(res2.ds, res2)
# resC = bch.PanelResult(res3.ds, res3)


# bench.report.append_tab(resA.to_panes())
# bench.report.append_tab(resB.to_panes())
# bench.report.append_tab(resC.to_panes())


bench.report.show()


# da = res.ds[res.result_vars[0].name].squeeze()

# print(da)
# print(da.values)

# print(da[:,0])

# print(res.ds)
# print(res.ds[res.result_vars[0].name].values)

exit()


# # da2 = da3.drop("z")

# da2 = da3[:,0]

# print(da3)

# print(da2)


# def pr(da: xr.DataArray):
#     print(da)
#     dim = len(da.sizes)
#     if dim > 0:
#         pr(da.drop_isel(da.dims[-1]))
#     print(dim)


# print(da)
#
# print(da.values)


# pr(da3)
# pr(da2)
