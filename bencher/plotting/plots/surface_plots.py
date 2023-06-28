import os
import errno
import matplotlib.pyplot as plt
import panel as pn
import numpy as np
import plotly.graph_objs as go
import holoviews as hv
import pandas as pd
import seaborn as sns
import plotly.express as px

import logging

from holoviews import opts
from bencher.bench_vars import ParametrizedSweep, ResultVar, ResultVec, ResultList
from bencher.bench_cfg import PltCfgBase, BenchCfg
from typing import List, Tuple
import seaborn as sns
import panel as pn
import matplotlib.pyplot as plt
import pandas as pd
from bencher.plotting.plot_filter import PlotFilter, VarRange, PlotInput
from bencher.plt_cfg import PltCfgBase
from bencher.plotting.plot_types import PlotTypes
hv.extension("plotly")

from textwrap import wrap

class SurfacePlot:
	# shared plot filter for catplots
    float_2_cat_0_vec_1_res_1 = PlotFilter(
        float_range=VarRange(2, 2),
        cat_range=VarRange(0, 0),
        vector_len=VarRange(1, 1),
        result_vars=VarRange(1, 1),
    )
	plot_surface_plotly_new
	def plot_surface_plotly(
		bench_cfg: BenchCfg, rv: ParametrizedSweep, xr_cfg: PltCfgBase
	) -> pn.pane.Plotly:
		"""Given a benchCfg generate a 2D surface plot

		Args:
			bench_cfg (BenchCfg): description of benchmark
			rv (ParametrizedSweep): result variable to plot
			xr_cfg (PltCfgBase): config of x,y variables

		Returns:
			pn.pane.Plotly: A 2d surface plot as a holoview in a pane
		"""

		if float_2_cat_0_vec_1_res_1.matches() type(rv) == ResultVec:
			return plot_scatter3D_px(bench_cfg, rv)

		bench_cfg = wrap_long_time_labels(bench_cfg)

		da = bench_cfg.ds[rv.name].transpose()

		mean = da.mean("repeat")

		x = da.coords[xr_cfg.x]
		y = da.coords[xr_cfg.y]

		opacity = 0.3

		surfaces = [go.Surface(x=x, y=y, z=mean)]

		if bench_cfg.repeats > 1:
			std_dev = da.std("repeat")
			surfaces.append(go.Surface(x=x, y=y, z=mean + std_dev, showscale=False, opacity=opacity))
			surfaces.append(go.Surface(x=x, y=y, z=mean - std_dev, showscale=False, opacity=opacity))

		eye_dis = 1.7
		layout = go.Layout(
			title=xr_cfg.title,
			width=700,
			height=700,
			scene=dict(
				xaxis_title=xr_cfg.xlabel,
				yaxis_title=xr_cfg.ylabel,
				zaxis_title=xr_cfg.zlabel,
				camera={"eye": {"x": eye_dis, "y": eye_dis, "z": eye_dis}},
			),
		)

		fig = {"data": surfaces, "layout": layout}

		return pn.pane.Plotly(fig)


	def plot_surface_holo(
		bench_cfg: BenchCfg, rv: ParametrizedSweep, xr_cfg: PltCfgBase
	) -> pn.pane.Plotly:
		"""Given a benchCfg generate a 2D surface plot

		Args:
			bench_cfg (BenchCfg): description of benchmark
			rv (ParametrizedSweep): result variable to plot
			xr_cfg (PltCfgBase): config of x,y variables

		Returns:
			pn.pane.holoview: A 2d surface plot as a holoview in a pane
		"""

		bench_cfg = wrap_long_time_labels(bench_cfg)

		alpha = 0.3

		da = bench_cfg.ds[rv.name]

		mean = da.mean("repeat")

		opts.defaults(
			opts.Surface(
				colorbar=True,
				width=800,
				height=800,
				zlabel=xr_cfg.zlabel,
				title=xr_cfg.title,
				# image_rtol=0.002,
			)
		)
		# TODO a warning suggests setting this parameter, but it does not seem to help as expected, leaving here to fix in the future
		# hv.config.image_rtol = 1.0

		ds = hv.Dataset(mean)
		surface = ds.to(hv.Surface)

		if bench_cfg.repeats > 1:
			std_dev = da.std("repeat")
			upper = hv.Dataset(mean + std_dev).to(hv.Surface).opts(alpha=alpha, colorbar=False)
			lower = hv.Dataset(mean - std_dev).to(hv.Surface).opts(alpha=alpha, colorbar=False)
			return surface * upper * lower
		return surface
