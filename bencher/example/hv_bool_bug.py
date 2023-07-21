import xarray as xr
import holoviews as hv
import panel as pn
from typing import List
import numpy as np


def create_dataarray(power_on_coord_range: List[str | bool]) -> hv.Bars:
    """Create a 2D dataarray where voltage is measured when the power_on = True and power_on =False for two samples and plot with hv.Bars

    Args:
        power_on_coord_range (List[str|bool]): List values to use as a coordinate
    """
    da = xr.DataArray(
        name="voltage",
        data=[[1.5, 1.6], [0.01, -0.02]],
        coords=dict(power_on=(power_on_coord_range), sample_num=([1, 2])),
    )

    hv_ds = hv.Dataset(da)
    print(f"datarray: {da}")
    print(f"dataframe: {da.to_dataframe()}")
    print(f"hv dataset: {hv_ds} ")
    return hv_ds.reduce(["sample_num"], np.mean).to(hv.Bars)


row = pn.Row()
# Create and plot a dataarray which uses strings as the index.  This works as expected
row.append(create_dataarray(power_on_coord_range=["True", "False"]))

# Create and plot the same data but use bools as the index.  This does not work because the values that have the index False do not appear in the holoviews dataset, even though they appear in the xarray dataset.  Bokeh warnings appear: BokehUserWarning: ColumnDataSource's columns must be of the same length. Current lengths: ('power_on', 1), ('voltage', 2).   These warnings occur because only data where power_on=True is included in the dataset but all the voltage data for both power_on=True and power_on=False is included
row.append(create_dataarray(power_on_coord_range=[True, False]))
row.show()
