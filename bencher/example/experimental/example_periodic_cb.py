import holoviews as hv
import panel as pn
from holoviews.streams import Stream

# Enable the ParamBokeh extension
hv.extension("bokeh", "param")


# Define a simple plot (replace this with your own plot)
def update_plot(value):
    # Your code to update the plot based on the slider value
    # Replace this with your own plot generation logic
    curve = hv.Curve([(x, x**value) for x in range(11)], kdims=["X"], vdims=["Y"])
    return curve


slider = pn.widgets.FloatSlider(name="Slider", start=0, end=10, value=0)
plot = hv.DynamicMap(
    update_plot, streams=[Stream.define("SliderValueStream", SliderValue=slider.param.value)]
)


# Create a PeriodicCallback to update the slider value
def periodic_callback():
    # Calculate the new slider value here
    new_value = slider.value + 0.1  # Example: Increment the slider value by 0.1
    if new_value > 10:
        new_value = 0  # Reset the slider value if it exceeds 10
    slider.value = new_value


# Create a PeriodicCallback that calls the periodic_callback function every 1000ms (1 second)
callback = pn.state.add_periodic_callback(periodic_callback, period=1000)

# Display the plot and slider
layout = pn.Column(plot, slider)
layout.show()
