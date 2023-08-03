import holoviews as hv
import numpy as np
import panel as pn

# hv.extension("bokeh", "plotly")
backend1 = "plotly"
# backend1 = "matplotlib"
backend2 = "bokeh"

# matplotlib.use("agg")

# hv.extension(backend1, backend2)
hv.extension(backend2, backend1)

# hv.extension(backend1)

# opts.defaults(opts.Surface(backend=backend1), opts.HeatMap(backend=backend2))

# hv.output(opts.Surface(backend=backend1), opts.HeatMap(backend=backend2))
# hv.output(surface.opts(fig_size=200, backend='matplotlib'), backend='matplotlib')

main = pn.Row()

# hv.output(backend="plotly")

dat = np.ones([10, 10])
# main.append(hv.Surface(dat))

surf = hv.Surface(dat)
main.append(hv.render(surf, backend=backend1))


# hv.output(backend="bokeh")
heat = hv.HeatMap(dat)
heat *= hv.Text(0, 0, "I only work with bokeh and matplotlib")
main.append(heat)

main.show()
