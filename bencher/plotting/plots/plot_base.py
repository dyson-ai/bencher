# from bencher import Pa#
import param


class PlotBase:
    def title(self, x: param.Parameter, y: param.Parameter, z: param.Parameter = None) -> str:
        if z is None:
            return f"{x.name} vs {y.name}"
        return f"{z.name} vs ({x.name} vs {y.name})"
