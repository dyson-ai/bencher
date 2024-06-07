import bencher as bch

import xarray as xr
import numpy as np
import panel as pn
import holoviews as hv


class ExampleMergeDataset(bch.ParametrizedSweep):

    value = bch.FloatSweep(default=0, bounds=[0, 10])
    repeats_x = bch.IntSweep(default=2, bounds=[2, 4])
    # repeats_y = bch.IntSweep(default=2, bounds=[2, 4])

    result_df = bch.ResultDataSet()

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        # self.result_df = xr.Dataset()
        # self.result_df = xr.Dataset({"dss": dss, "nmap": (("x"), nmap)})
        # First, create a DataArray from the vector
        vector = [v + self.value for v in range(1, self.repeats_x)]
        # print(vector)
        data_array = xr.DataArray(vector, dims=["index"], coords={"index": np.arange(len(vector))})
        # Convert the DataArray to a Dataset
        result_df = xr.Dataset({"result_df": data_array})
        self.result_df = pn.panel(result_df)
        self.result_df = bch.ResultDataSet(result_df.to_pandas())
        return super().__call__(**kwargs)


def example_dataset(run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None):
    bench = ExampleMergeDataset().to_bench(run_cfg, report)

    # res =bench.plot_sweep()

    # res = bench.plot_sweep(input_vars=[bch.p("value", range(0, 3))], const_vars=dict(repeats_x=4))
    res = bench.plot_sweep(input_vars=["value"], const_vars=dict(repeats_x=4))

    # bench.report.append(res.to_panes(target_dimension=1))
    # bench.report.append(res.to_panes(target_dimension=2))

    # bench.reprt.append(res.to_video_grid
    #                             # bch.BenchResult.to_video_grid,
    #     target_duration=0.06,
    #     compose_method_list=[
    #         bch.ComposeType.right,
    #         bch.ComposeType.right,
    #         bch.ComposeType.sequence,
    #     ],
    # )

    # bench.report.append(res.to_panes(container=hv.Bars,target_dimension=1))
    # bench.report.append(res.to_panes(container=hv.Curve))

    bench.report.append(res.to_dataset1(container=hv.Curve))


    return bench


if __name__ == "__main__":
    example_dataset().report.show()

    # bench_runner = bch.BenchRunner("a")
    # bench_runner.add_run(example_dataset)
    # bench_runner.run(show=True)
