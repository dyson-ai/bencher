from bencher.results.panel_result import PanelResult


class BenchResult(PanelResult):
    def __init__(self, **params):
        super().__init__(**params)
