import bencher as bch
from bencher.example.meta.example_meta import BenchMeta

bench = BenchMeta().to_bench(bch.BenchRunCfg())
bench.plot_sweep(input_vars=[], const_vars={"float_vars": 2, "level": 5})
bench.report.show()
