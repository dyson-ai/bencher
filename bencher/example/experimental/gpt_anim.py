import random
import panel as pn
import datetime as dt
import holoviews as hv
import time
from holoviews.streams import Pipe

hv.extension("bokeh")
pn.extension()


latest_update = pn.widgets.StaticText()

# define a pip funtionn for streams the data
pipe = Pipe(data=[])
dmap = hv.DynamicMap(hv.Bars, streams=[pipe])

# init the data
x, y = [x for x in range(10)], [random.randint(0, 100) for y in range(10)]
pipe.send((x, y))


# define the update funtion
def update_plot():
    latest_update.value = f'updating: {dt.datetime.now().strftime("%c")}'
    time.sleep(0.5)
    x, y = [x for x in range(10)], [random.randint(0, 100) for y in range(10)]
    pipe.send((x, y))
    latest_update.value = f'latest: {dt.datetime.now().strftime("%c")}'


# period call back
cb = pn.state.add_periodic_callback(update_plot, period=2000, start=False)

# define the start and stop button
button = pn.widgets.Button(name="Click to Start", button_type="success")


def button_click(event):
    if button.name == "Click to Start":
        print("started")
        cb.start()
        button.name = "started"
        button.button_type = "danger"
    else:
        print("stoped")
        cb.stop()
        button.name = "Click to Start"
        button.button_type = "success"


button.on_click(button_click)

# layout
pn.Column(button, pn.Column(dmap), latest_update).show()
