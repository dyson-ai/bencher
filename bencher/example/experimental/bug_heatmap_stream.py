import pandas as pd
import holoviews as hv
import panel as pn

hv.extension("bokeh")


# create 2x2 dataset with integer keys for key1 and key2
df_integer = pd.DataFrame(
    ([[0, 0, 10], [0, 1, 20], [1, 0, 20], [1, 1, 30]]), columns=["key1", "key2", "value"]
)

# create 2x2 dataset with an integer key for key1 and a string key for key2
df_categorical = pd.DataFrame(
    ([[0, "A", 10], [0, "B", 20], [1, "A", 20], [1, "B", 30]]), columns=["key1", "key2", "value"]
)


def move_pointer(x, y):
    pass
    print(x, y)


def create_heatmap_streamxy(df: pd.DataFrame):
    """Take a dataframe and return a heatmap that has a streamxy callback."""
    ds = hv.Dataset(df)

    heatmap = ds.to(hv.HeatMap, kdims=["key1", "key2"], vdims="value").opts(tools=["hover"])
    hv.streams.PointerXY(source=heatmap).add_subscriber(move_pointer)
    hv.streams.Hover
    return heatmap


row = pn.Row()
row.append(create_heatmap_streamxy(df_integer))
row.append(create_heatmap_streamxy(df_categorical))
row.show()

#moving the mouse from inside the heatmap to over the top edge causes an index exception for the categorical plot 
# Task exception was never retrieved
# future: <Task finished name='Task-302' coro=<Callback.process_on_event() done, defined at /usr/local/lib/python3.10/site-packages/holoviews/plotting/bokeh/callbacks.py:328> exception=IndexError('list index out of range')>
# Traceback (most recent call last):
#   File "/usr/local/lib/python3.10/site-packages/holoviews/plotting/bokeh/callbacks.py", line 351, in process_on_event
#     self.on_msg(msg)
#   File "/usr/local/lib/python3.10/site-packages/holoviews/plotting/bokeh/callbacks.py", line 203, in on_msg
#     processed_msg = self._process_msg(filtered_msg)
#   File "/usr/local/lib/python3.10/site-packages/holoviews/plotting/bokeh/callbacks.py", line 503, in _process_msg
#     msg['y'] = y_range.factors[int(msg['y'])]
# IndexError: list index out of range
