# -*- coding: utf-8 -*-
"""
An example of a simple player widget animating an Image demonstrating
how to connect a simple HoloViews plot with custom widgets and
combine them into a bokeh layout.

The app can be served using:

    bokeh serve --show player.py

"""
import numpy as np
import holoviews as hv

from bokeh.io import curdoc
from bokeh.document import Document
from bokeh.layouts import layout
from bokeh.models import Slider, Button
import panel as pn

# Declare the HoloViews object
start = 0
end = 10
hmap = hv.HoloMap({i: hv.Image(np.random.rand(10,10)) for i in range(start, end+1)})



class HoloMapPlayer:

    def __init__(self,hmap) -> None:
        renderer = hv.renderer('bokeh')
        # Convert the HoloViews object into a plot
        self.plot = renderer.get_plot(hmap)
        self.slider = Slider(start=start, end=end, value=0, step=1, title="Year")
        self.slider.on_change('value', self.slider_update)
        self.button = Button(label='► Play', width=60)
        self.button.on_click(self.animate)

         # Combine the bokeh plot on plot.state with the widgets
        self.layout = layout([
        [self.plot.state],
        [self.slider, self.button],
    ], sizing_mode='fixed')

        curdoc().add_root(self.layout)

        # self.pane = pn.Row(self.lay)


    

    def animate_update(self):
        year = self.slider.value + 1
        if year > end:
            year = start
        self.slider.value = year

    def slider_update(self,attrname, old, new):
        self.plot.update(self.slider.value)

    

    def animate(self):
        if self.button.label == '► Play':
            self.button.label = '❚❚ Pause'
            curdoc().add_periodic_callback(self.animate_update, 200)
        else:
            self.button.label = '► Play'
            curdoc().remove_periodic_callback(self.animate_update)

  
    def show(self):
        # pn.Row(curdoc()).show()
        pn.Row(self.layout).show()


   
hmp = HoloMapPlayer(hmap)

hmp.show()

