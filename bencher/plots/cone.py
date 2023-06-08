class SurfacePlot(PlotSignature):
    def get_plot_signatures(self):
        plot_sig = PlotSignature()
        plot_sig.float_cnt = VarRange(2, 2)
        plot_sig.cat_range = VarRange(0, 0)
        plot_sig.vector_len = VarRange(2, 2)
        return plot_sig
	def plot_cone_plotly(
	bench_cfg: BenchCfg, rv: ParametrizedOutput, xr_cfg: PltCfgBase
	) -> pn.pane.Plotly:
	"""Given a benchCfg generate a 3D surface plot

	Args:
		bench_cfg (BenchCfg): description of benchmark
		rv (ParametrizedOutput): result variable to plot
		xr_cfg (PltCfgBase): config of x,y variables

	Returns:
		pn.pane.Plotly: A 3d volume plot as a holoview in a pane
	"""

	bench_cfg = wrap_long_time_labels(bench_cfg)

	names = rv.index_names()

	# da = bench_cfg.ds[names[0]]

	opacity = 1.0

	df = bench_cfg.ds.to_dataframe().reset_index()

	print("size before removing zero size vectors", df.shape)
	df = df.loc[(df[names[0]] != 0.0) | (df[names[1]] != 0.0) | (df[names[2]] != 0.0)]
	print("size after removing zero size vectors", df.shape)

	data = [
		go.Cone(
		x=df[xr_cfg.x],
		y=df[xr_cfg.y],
		z=df[xr_cfg.z],
		u=df[names[0]],
		v=df[names[1]],
		w=df[names[2]],
		# sizemode="absolute",
		# sizeref=2,
		anchor="tail",
		opacity=opacity,
		)
	]

	layout = go.Layout(
		title=f"{rv.name} vs ({xr_cfg.x} vs {xr_cfg.y} vs {xr_cfg.z})",
		autosize=True,
		width=700,
		height=700,
		margin=dict(t=50, b=50, r=50, l=50),
		scene=dict(
		xaxis_title=xr_cfg.xlabel,
		yaxis_title=xr_cfg.ylabel,
		zaxis_title=rv.name,
		),
	)

	fig = dict(data=data, layout=layout)

	return pn.pane.Plotly(fig)
