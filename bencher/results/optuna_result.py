from typing import List

import numpy as np
import optuna
import panel as pn
import param
from optuna.visualization import (
    plot_param_importances,
    plot_pareto_front,
    plot_optimization_history,
)

from bencher.bench_cfg import BenchCfg


from bencher.variables.inputs import IntSweep, FloatSweep, StringSweep, EnumSweep, BoolSweep
from bencher.variables.time import TimeSnapshot, TimeEvent
from bencher.variables.results import OptDir

from bencher.variables.parametrised_sweep import ParametrizedSweep

import panel as pn
import plotly.graph_objs as go

from bencher.plotting.plot_types import PlotTypes
from bencher.results.bench_result_base import BenchResultBase
from bencher.optuna_conversions import *
from bencher.optuna_conversions import bench_cfg_to_study, collect_optuna_plots
from bencher.utils import hmap_canonical_input


class OptunaResult(BenchResultBase):
    def to_optuna(self) -> List[pn.pane.panel]:
        """Create an optuna summary from the benchmark results

        Returns:
            List[pn.pane.panel]: A list of optuna plot summarising the benchmark process
        """

        return collect_optuna_plots(self.bench_cfg)

    # def to_optuna_from_sweep(self,worker)
    #     return self.to_optuna_from_sweep(bench_cfg, n_trials)

    
