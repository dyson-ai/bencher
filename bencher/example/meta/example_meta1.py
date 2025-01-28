import bencher as bch
from bencher.example.meta.example_meta import BenchMeta

bench = BenchMeta().to_bench(bch.BenchRunCfg())

bench.plot_sweep(
    title="Meta Bench",
    description="""## All Combinations of Variable Sweeps and Resulting Plots
This uses bencher to display all the combinations of plots bencher is able to produce""",
    input_vars=[
        bch.p("float_vars", [2]),
    ],
    # input_vars=[],
    const_vars={"float_vars":1,"level":5}
)


bench.report.show()