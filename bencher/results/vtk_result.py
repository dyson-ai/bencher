import panel as pn
import plotly.graph_objs as go
from typing import Optional
import xarray as xr

from param import Parameter

from bencher.plotting.plot_filter import VarRange
from bencher.results.bench_result_base import BenchResultBase, ReduceType
from bencher.variables.results import ResultVar

# import vtk
# from vtkmodules.vtkCommonDataModel import vtkImageData


# import vtk
import numpy as np
# from vtk.util import numpy_support

pn.extension('vtk')



def numpy_array_as_vtk_image_data(source_numpy_array):
    """
    :param source_numpy_array: source array with 2-3 dimensions. If used, the third dimension represents the channel count.
    Note: Channels are flipped, i.e. source is assumed to be BGR instead of RGB (which works if you're using cv2.imread function to read three-channel images)
    Note: Assumes array value at [0,0] represents the upper-left pixel.
    :type source_numpy_array: np.ndarray
    :return: vtk-compatible image, if conversion is successful. Raises exception otherwise
    :rtype vtk.vtkImageData
    """

    if len(source_numpy_array.shape) > 2:
        channel_count = source_numpy_array.shape[2]
    else:
        channel_count = 1

    output_vtk_image = vtk.vtkImageData()
    output_vtk_image.SetDimensions(
        source_numpy_array.shape[1], source_numpy_array.shape[0], channel_count
    )

    vtk_type_by_numpy_type = {
        np.uint8: vtk.VTK_UNSIGNED_CHAR,
        np.uint16: vtk.VTK_UNSIGNED_SHORT,
        np.uint32: vtk.VTK_UNSIGNED_INT,
        np.uint64: vtk.VTK_UNSIGNED_LONG
        if vtk.VTK_SIZEOF_LONG == 64
        else vtk.VTK_UNSIGNED_LONG_LONG,
        np.int8: vtk.VTK_CHAR,
        np.int16: vtk.VTK_SHORT,
        np.int32: vtk.VTK_INT,
        np.int64: vtk.VTK_LONG if vtk.VTK_SIZEOF_LONG == 64 else vtk.VTK_LONG_LONG,
        np.float32: vtk.VTK_FLOAT,
        np.float64: vtk.VTK_DOUBLE,
    }
    vtk_datatype = vtk_type_by_numpy_type[source_numpy_array.dtype.type]

    source_numpy_array = np.flipud(source_numpy_array)

    # Note: don't flip (take out next two lines) if input is RGB.
    # Likewise, BGRA->RGBA would require a different reordering here.
    if channel_count > 1:
        source_numpy_array = np.flip(source_numpy_array, 2)

    depth_array = numpy_support.numpy_to_vtk(
        source_numpy_array.ravel(), deep=True, array_type=vtk_datatype
    )
    depth_array.SetNumberOfComponents(channel_count)
    output_vtk_image.SetSpacing([1, 1, 1])
    output_vtk_image.SetOrigin([-1, -1, -1])
    output_vtk_image.GetPointData().SetScalars(depth_array)

    output_vtk_image.Modified()
    return output_vtk_image


class VTKResult(BenchResultBase):
    def to_vtk(self, result_var: Parameter = None, **kwargs):
        return self.filter(
            self.to_vtk_da,
            float_range=VarRange(3, 3),
            cat_range=VarRange(-1, 0),
            reduce=ReduceType.REDUCE,
            target_dimension=3,
            result_var=result_var,
            result_types=(ResultVar),
            **kwargs,
        )

    def to_vtk_da(
        self, dataset: xr.Dataset, result_var: Parameter, width=600, height=600
    ) -> Optional[pn.pane.Plotly]:
        
        import vtk
        from vtk.util.colors import tomato

        # This creates a polygonal cylinder model with eight circumferential
        # facets.
        cylinder = vtk.vtkCylinderSource()
        cylinder.SetResolution(8)

        # The mapper is responsible for pushing the geometry into the graphics
        # library. It may also do color mapping, if scalars or other
        # attributes are defined.
        cylinderMapper = vtk.vtkPolyDataMapper()
        cylinderMapper.SetInputConnection(cylinder.GetOutputPort())

        # The actor is a grouping mechanism: besides the geometry (mapper), it
        # also has a property, transformation matrix, and/or texture map.
        # Here we set its color and rotate it -22.5 degrees.
        cylinderActor = vtk.vtkActor()
        cylinderActor.SetMapper(cylinderMapper)
        cylinderActor.GetProperty().SetColor(tomato)
        # We must set ScalarVisibilty to 0 to use tomato Color
        cylinderMapper.SetScalarVisibility(0)
        cylinderActor.RotateX(30.0)
        cylinderActor.RotateY(-45.0)

        # Create the graphics structure. The renderer renders into the render
        # window.
        ren = vtk.vtkRenderer()
        renWin = vtk.vtkRenderWindow()
        renWin.AddRenderer(ren)

        # Add the actors to the renderer, set the background and size
        ren.AddActor(cylinderActor)
        ren.SetBackground(0.1, 0.2, 0.4)

        geom_pane = pn.pane.VTK(renWin, width=500, height=500)
        return geom_pane
        
        # import pyvista as pv
        # from pyvista import examples

        # # Download a volumetric dataset
        # vol = examples.download_head()
        # volume = pn.pane.VTKVolume(vol, height=600, sizing_mode='stretch_width', display_slices=True)
        # return volume
        """Given a benchCfg generate a 3D surface plot
        Returns:
            pn.pane.Plotly: A 3d volume plot as a holoview in a pane
        """
        x = self.bench_cfg.input_vars[0]
        y = self.bench_cfg.input_vars[1]
        z = self.bench_cfg.input_vars[2]
        opacity = 0.1
        meandf = dataset[result_var.name].to_dataframe().reset_index()


        data_matrix = np.zeros([75, 75, 75], dtype=np.uint8)
        data_matrix[0:35, 0:35, 0:35] = 50
        data_matrix[25:55, 25:55, 25:55] = 100
        data_matrix[45:74, 45:74, 45:74] = 150

        data_matrix = dataset[result_var.name].data

        print("loading vtk")


        return pn.pane.VTKVolume(data_matrix, width=800, height=600, spacing=(3,2,1), interpolation='nearest', edge_gradient=0, sampling=0)

        # vtkim = vtkImageData()

        # vtkim.SetFieldData()

        # vtkim = numpy_array_as_vtk_image_data(dataset[result_var.name].data)

        # return

        # data = [
        #     go.Volume(
        #         x=meandf[x.name],
        #         y=meandf[y.name],
        #         z=meandf[z.name],
        #         value=meandf[result_var.name],
        #         isomin=meandf[result_var.name].min(),
        #         isomax=meandf[result_var.name].max(),
        #         opacity=opacity,
        #         surface_count=20,
        #     )
        # ]

        # layout = go.Layout(
        #     title=f"{result_var.name} vs ({x.name} vs {y.name} vs {z.name})",
        #     width=width,
        #     height=height,
        #     margin=dict(t=50, b=50, r=50, l=50),
        #     scene=dict(
        #         xaxis_title=f"{x.name} [{x.units}]",
        #         yaxis_title=f"{y.name} [{y.units}]",
        #         zaxis_title=f"{z.name} [{z.units}]",
        #     ),
        # )

        # fig = dict(data=data, layout=layout)

        # return pn.pane.Plotly(fig, name="volume_plotly")
