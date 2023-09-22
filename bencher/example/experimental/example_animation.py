import numpy as np
import holoviews as hv
from bokeh.models import Button
import panel as pn


class HoloMapPlayer:
    def __init__(self, holomap, slider=None, fps=10.0) -> None:
        renderer = hv.renderer("bokeh")

        #THIS IS THE LINE I NEED TO CHANGE
        self.plot = renderer.get_plot(holomap) 

        self.holomap = holomap
        
        if slider is None:
            self.slider = pn.widgets.DiscreteSlider(options=holomap.keys())
        else:
            self.slider = slider

        self.holomap_index=0

        self.bound_slider = pn.bind(self.slider_update, self.slider)
        self.button = Button(label="► Play", width=60)
        self.button.on_click(self.animate)
        self.ms_update = int(1.0 / fps)

        self.layout = pn.Column()
        self.layout.append(self.plot.state)
        self.layout.append(self.slider)
        self.layout.append(self.bound_slider)
        self.layout.append(self.button)

        self.cb = pn.state.add_periodic_callback(self.animate_update, self.ms_update, start=False)

    def animate_update(self):
        self.holomap_index = (self.holomap_index+1)%len(self.holomap.keys())        
        self.slider.value = self.holomap_index

    def slider_update(self, *args, **kwargs):
        self.plot.update(self.slider.value)

        #I WOULD LIKE SOMETHING LIKE THIS
        # return self.holomap[self.slider.value]

    def animate(self) -> None:
        if self.button.label == "► Play":
            self.button.label = "❚❚ Pause"
            self.cb.start()
        else:
            self.button.label = "► Play"
            self.cb.stop()

    def show(self) -> None:
        pn.Row(self.layout).show()


if __name__ == "__main__":
    start = 0
    end = 10
    hmap = hv.HoloMap({i: hv.Image(np.random.rand(10, 10)) for i in range(start, end + 1)})

    HoloMapPlayer(hmap, fps=30).show()
