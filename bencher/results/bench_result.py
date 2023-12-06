from bencher.results.panel_result import PanelResult


class BenchResult(PanelResult):
    def __init__(self, xr_dataset) -> None:
        PanelResult.__init__(self,xr_dataset)
