import xarray as xr
import holoviews as hv
import panel as pn

hv.extension("bokeh")

# Example data matching your structure:
# - "index": the coordinate (dimension)
# - "output": the central (y) values
# - "output_std": the spread (error) around y
ds = xr.Dataset(
    data_vars={
        "output": ("index", [0.0, 1.0, 1.0, 1.0, 1.0, 1.5]),  # Central values
        "output_std": ("index", [0.0, 0.0, 0.0, 0.7071, 1.0, 0.5]),  # Spread (error)
    },
    coords={"index": [0, 1, 2, 3, 4, 5]},  # Index as coordinate
)
print(ds)

# Wrap the xarray.Dataset in an hv.Dataset and declare which dims are 'kdims' vs 'vdims'.
# Here:
#   - kdims=['index'] means index is our x-axis
#   - vdims=['output','output_std'] means these are our value dims
# hvds = hv.Dataset(ds, kdims=["index"], vdims=["output", "output_std"])

hvds = hv.Dataset(ds)
print(hvds)

# Convert to a Spread plot:
#   - x dimension = 'index'
#   - y dimension = 'output'
#   - spread dimension = 'output_std'
# spread_plot = hvds.to(hv.Spread, 'index', 'output', 'output_std')
spread_plot = hvds.to(hv.Spread)

# Alternatively, you could create the Spread element directly:
# spread_plot = hv.Spread((ds.index, ds.output, ds.output_std),
#                         kdims=["index"], vdims=["output","output_std"])

# Display the plot using Panel
pn.Row(spread_plot).show()
