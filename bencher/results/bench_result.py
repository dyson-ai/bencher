# from bencher.bench_cfg import BenchCfg
from bencher.results.panel_result import PanelResult
from bencher.results.result_plotly import ResultPlotly

# from bencher.results.bench_result_base import BenchResultBase


class BenchResult(PanelResult,ResultPlotly):
    """Contains the results of the benchmark and has methods to cast the results to various datatypes and graphical representations"""

    def __init__(self, bench_cfg) -> None:
        PanelResult.__init__(self, bench_cfg)
        ResultPlotly.__init__(self, bench_cfg)
