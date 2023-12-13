from bencher.results.panel_result import PanelResult


class BenchResult(PanelResult):
    def __init__(self, bench_cfg) -> None:
        PanelResult.__init__(self, bench_cfg)
