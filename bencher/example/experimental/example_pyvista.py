import pyvista as pv
import panel as pn

plotter = pv.Plotter()  # we define a pyvista plotter
plotter.background_color = (0.1, 0.2, 0.4)
# we create a `VTK` panel around the render window
geo_pan_pv = pn.panel(plotter.ren_win, width=500, height=500)
