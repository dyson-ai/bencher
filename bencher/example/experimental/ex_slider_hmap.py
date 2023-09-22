import holoviews as hv
import numpy as np
import random
import panel as pn
hv.extension('bokeh')
from holoviews.streams import Stream, param

# Generate Your Data
x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)

start = 0
end = 10
holomap = hv.HoloMap({i: hv.Image(np.random.rand(10, 10)) for i in range(start, end + 1)})


# Define a Callback Function
def update_plot(frame):
    return holomap[frame]


def animate():
    return random.randint (0,5)

Time = Stream.define('Time', t=param.Number(default=0.0, doc='A time parameter'))

# Create a Slider
# slider = hv.streams.Stream.define('Frame', Frame=1)
# slider_widget = hv.DynamicMap(update_plot, streams=[slider])
slider_widget = hv.DynamicMap(update_plot,kdims=["frame"])

slider_widget = slider_widget.redim.range(frame=(start,end))

def cur_key():
    print(slider_widget.current_key)
    slider_widget.event((4,))
    slider_widget.current_key= (4,)
    slider_widget.apply()

pn.state.add_periodic_callback(cur_key)


# Display the Plot and Slider
# plot = slider_widget.opts(plot=opts.Curve(width=800, height=400)) * holomap
# plot.opts(plot=opts.Overlay(show_legend=False))
# layout = plot + slider
# layout = plot 

pn.Row(slider_widget).show()


# Show the Plot
# layout.show()
