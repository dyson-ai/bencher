from __future__ import annotations
from typing import Callable, List
import param
from bencher.bench_cfg import BenchCfg
from bencher.variables.results import PANEL_TYPES

from bencher.variables.inputs import IntSweep, FloatSweep, BoolSweep, EnumSweep, StringSweep
from bencher.variables.time import TimeSnapshot


class PltCfgBase(param.Parameterized):
    """A base class that contains plotting parameters shared by seaborn and xarray"""

    x: str = param.String(None, doc="the x parameter for seaborn and xarray plotting functions")
    y: str = param.String(None, doc="the y parameter for seaborn and xarray plotting functions")
    z: str = param.String(None, doc="the z parameter for xarray plotting functions")
    hue: str = param.String(None, doc="the hue parameter for seaborn and xarray plotting functions")

    row: str = param.String(None, doc="the row parameter for seaborn and xarray plotting functions")
    col: str = param.String(None, doc="the col parameter for seaborn and xarray plotting functions")

    num_rows: int = param.Integer(1, doc="The number of rows in the facetgrid")
    num_cols: int = param.Integer(1, doc="The number of cols in the facetgrid")

    kind: str = param.String(None, doc="the 'kind' of plot, ie barplot, lineplot, scatter etc")
    marker: str = param.String(None, doc="The marker to use when plotting")

    cmap = param.String(None, doc="colormap type")

    plot_callback_sns: Callable = None
    plot_callback_xra: Callable = None
    plot_callback: Callable = None

    xlabel: str = param.String(None, doc="The label for the x-axis")
    ylabel: str = param.String(None, doc="The label for the y-axis")
    zlabel: str = param.String(None, doc="The label for the z-axis")

    title: str = param.String(None, doc="The title of the graph")

    width: int = param.Integer(700, doc="Width of the plot in pixels")
    height: int = param.Integer(700, doc="Height of the plot in pixels")

    def as_dict(self, include_params: List[str] = None, exclude_params: List[str] = None) -> dict:
        """Return this class as dictionary to pass to plotting functions but exclude parameters that are not expected by those functions

        Args:
            include_params (List[str], optional): a list of property names to include. Defaults to None.
            exclude_params (List[str], optional): a list of property names to exclude. Defaults to None.

        Returns:
            dict: a dictionary of plotting arguments
        """
        all_params = self.param.values()
        all_params.pop("name")

        output = {}
        if include_params is not None:
            for i in include_params:
                output[i] = all_params[i]
        else:
            output = all_params

        if exclude_params is not None:
            for e in exclude_params:
                output.pop(e)

        return output

    def as_sns_args(self) -> dict:
        return self.as_dict(include_params=["x", "y", "hue", "row", "col", "kind"])


class PltCntCfg(param.Parameterized):
    """Plot Count Config"""

    float_vars = param.List(doc="A list of float vars in order of plotting, x then y")
    float_cnt = param.Integer(0, doc="The number of float variables to plot")
    cat_vars = param.List(doc="A list of categorical values to plot in order hue,row,col")
    cat_cnt = param.Integer(0, doc="The number of cat variables")
    vector_len = param.Integer(1, doc="The vector length of the return variable , scalars = len 1")
    result_vars = param.Integer(1, doc="The number result variables to plot")  # todo remove
    panel_vars = param.List(doc="A list of panel results")
    panel_cnt = param.Integer(0, doc="Number of results reprented as panel panes")
    repeats = param.Integer(0, doc="The number of repeat samples")
    inputs_cnt = param.Integer(0, doc="The number of repeat samples")

    print_debug = param.Boolean(
        True, doc="Print debug information about why a filter matches this config or not"
    )

    @staticmethod
    def generate_plt_cnt_cfg(
        bench_cfg: BenchCfg,
    ) -> PltCntCfg:
        """Given a BenchCfg work out how many float and cat variables there are and store in a PltCntCfg class

        Args:
            bench_cfg (BenchCfg): See BenchCfg definition

        Raises:
            ValueError: If no plotting procedure could be automatically detected

        Returns:
            PltCntCfg: see PltCntCfg definition
        """
        plt_cnt_cfg = PltCntCfg()
        # plt_cnt_cfg.float_vars = deepcopy(bench_cfg.iv_time)

        plt_cnt_cfg.cat_vars = []
        plt_cnt_cfg.float_vars = []

        for iv in bench_cfg.input_vars:
            if isinstance(iv, (IntSweep, FloatSweep, TimeSnapshot)):
                # if "IntSweep" in typestr or "FloatSweep" in typestr:
                plt_cnt_cfg.float_vars.append(iv)
                type_allocated = True
            if isinstance(iv, (EnumSweep, BoolSweep, StringSweep)):
                # if "EnumSweep" in typestr or "BoolSweep" in typestr or "StringSweep" in typestr:
                plt_cnt_cfg.cat_vars.append(iv)
                type_allocated = True

            if not type_allocated:
                raise ValueError(f"No rule for type {type(iv)}")

        for rv in bench_cfg.result_vars:
            if isinstance(rv, PANEL_TYPES):
                plt_cnt_cfg.panel_vars.append(rv)

        plt_cnt_cfg.float_cnt = len(plt_cnt_cfg.float_vars)
        plt_cnt_cfg.cat_cnt = len(plt_cnt_cfg.cat_vars)
        plt_cnt_cfg.panel_cnt = len(plt_cnt_cfg.panel_vars)
        plt_cnt_cfg.repeats = bench_cfg.repeats
        plt_cnt_cfg.inputs_cnt = len(bench_cfg.input_vars)
        return plt_cnt_cfg

    def __str__(self):
        return f"float_cnt: {self.float_cnt}\ncat_cnt: {self.cat_cnt} \npanel_cnt: {self.panel_cnt}\nvector_len: {self.vector_len}"
