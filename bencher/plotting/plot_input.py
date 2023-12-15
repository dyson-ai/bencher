from __future__ import annotations

from dataclasses import dataclass

from bencher.results.bench_result import BenchResult
from bencher.variables.parametrised_sweep import ParametrizedSweep

from bencher.plotting.plt_cnt_cfg import PltCntCfg


@dataclass
class PlotInput:
    """A dataclass that contains all the information needed to plot
    Args:
        bench_cfg (BenchCfg): The benchmark configuration used to generate the result data
        rv (ParametrizedSweep): The result variable to plot
        plt_cnt_cfg (PltCntCfg): The number and types of variable to plot
    """

    bench_res: BenchResult
    rv: ParametrizedSweep
    plt_cnt_cfg: PltCntCfg
