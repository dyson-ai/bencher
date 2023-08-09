# import holoviews as hv
# import numpy as np
# import param
# from holoviews import opts, streams
# from holoviews.plotting.links import DataLink

# import panel as pn

# hv.extension("bokeh")

# datasets = {
#     "data1": np.random.randint(1, 10, size=(4, 2)),
#     "data2": np.random.randint(1, 10, size=(4, 2)),
# }

# other_data = {i: np.random.randint(1, 10, size=(100, 100)) for i in range(4)}


# class Explorer(param.Parameterized):
#     dataset = param.ObjectSelector(default=list(datasets.keys())[0], objects=list(datasets.keys()))

#     lines = param.Boolean(default=False)

#     # streams
#     stream = param.ClassSelector(
#         default=streams.PointDraw(drag=False, add=False), class_=(streams.PointDraw), precedence=-1
#     )

#     selection = param.ClassSelector(
#         default=streams.Selection1D(), class_=(streams.Selection1D), precedence=-1
#     )

#     @param.depends("dataset")
#     def load_file(self):
#         name = self.dataset
#         datum = datasets[name]
#         scatter = hv.Scatter(datum).opts(size=8)

#         # update the PointDraw/Selection1D sources/data
#         self.stream.source = scatter
#         self.selection.source = scatter
#         self.stream.update(data=scatter.columns())  # reset PointDraw data
#         self.selection.update(index=[])  # reset selection index

#         table = hv.Table(scatter).opts(index_position=False, editable=True, selectable=True)
#         DataLink(scatter, table)

#         return (scatter + table).opts(
#             opts.Scatter(tools=["tap", "hover", "box_select"]), opts.Table(editable=True)
#         )

#     @param.depends("dataset", "selection.index", "lines")
#     def view(self):
#         """update 3rd plot whenever dataset, selection.index, or lines is changed"""
#         if self.selection.index == []:
#             return None
#         else:
#             # modify with your "other" data
#             if self.lines is True:
#                 return hv.Path(other_data[self.selection.index[0]]).opts(shared_axes=False)

#         return hv.operation.datashader.regrid(
#             hv.Image(other_data[self.selection.index[0]]),
#             upsample=True,
#             interpolation="bilinear",
#         ).opts(shared_axes=False)

#     @param.depends("stream.data", watch=True)
#     def update_data(self):
#         """update dataset whenever a point is deleted using PointDraw"""
#         datasets[self.dataset] = np.vstack((self.stream.data["x"], self.stream.data["y"])).T


# explorer = Explorer()
# pn.Row(pn.Column(explorer.param, explorer.view), explorer.load_file).show()
