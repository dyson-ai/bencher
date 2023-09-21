from functools import partial

import numpy as np
import panel as pn

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure


def update(source):
    data = np.random.randint(0, 2**31, 10)
    source.data.update({"y": data})


def panel_app():
    source = ColumnDataSource({"x": np.arange(10), "y": np.arange(10)})
    p = figure()
    p.line(x="x", y="y", source=source)
    cb = pn.state.add_periodic_callback(partial(update, source), 200, timeout=5000)
    toggle = pn.widgets.Toggle(name="Toggle callback", value=True)
    toggle.link(cb, bidirectional=True, value="running")
    return pn.Column(pn.pane.Bokeh(p), toggle)


pn.serve(panel_app)
