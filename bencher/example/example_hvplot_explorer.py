# THIS IS NOT A WORKING EXAMPLE YET
# pylint: disable=duplicate-code
from bencher import Bench, BenchRunCfg, ExampleBenchCfgIn, ExampleBenchCfgOut, bench_function
import hvplot

bench = Bench("Bencher_Example_Simple", bench_function, ExampleBenchCfgIn)


if __name__ == "__main__":
    bench_out = bench.plot_sweep(
        input_vars=[ExampleBenchCfgIn.param.theta, ExampleBenchCfgIn.param.offset],
        result_vars=[ExampleBenchCfgOut.param.out_sin],
        title="Float 1D Example",
        description="""Bencher is a tool to make it easy to explore how input parameter affect a range of output metrics.  In these examples we are going to benchmark an example function which has been selected to show the features of bencher.
        The example function takes an input theta and returns the absolute value of sin(theta) and cos(theta) +- various types of noise.

        def bench_function(cfg: ExampleBenchCfgIn) -> ExampleBenchCfgOut:
            "Takes an ExampleBenchCfgIn and returns a ExampleBenchCfgOut output"
            out = ExampleBenchCfgOut()
            noise = calculate_noise(cfg)
            offset = 0.0

            postprocess_fn = abs if cfg.postprocess_fn == PostprocessFn.absolute else negate_fn

            out.out_sin = postprocess_fn(offset + math.sin(cfg.theta) + noise)
            out.out_cos = postprocess_fn(offset + math.cos(cfg.theta) + noise)
            return out
        """,
        post_description="Here you can see the output plot of sin theta between 0 and pi.  In the tabs at the top you can also view 3 tabular representations of the data",
        run_cfg=BenchRunCfg(
            auto_plot=True,
            use_cache=False,
            repeats=2,
        ),
    )

    hvexplorer = hvplot.explorer(bench_out.get_dataframe())
    hvexplorer.show()
