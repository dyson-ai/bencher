from vedo import Volume, show
import numpy as np

# Create the isosurface browser
vol = np.random.rand(30, 30, 30)
volActor = Volume(vol)
iso = Volume(vol).isosurface().c("tomato")

# Create the slicer 3D plotter
slicer = Volume(vol).isosurface().c("green")

# Show both plots side by side
show([(volActor, iso), slicer], N=2, axes=1)
