import math
import numpy as np
from dataclasses import dataclass
import bencher as bch


@dataclass
class V3:
    x: float
    y: float
    z: float
    distance: float

    def __call__(self):
        self.distance = math.pow(np.linalg.norm(np.array([self.x, self.y, self.z])), 2)


def distance(x=0, y=0, z=0):
    return math.pow(np.linalg.norm(np.array([x, y, z])), 2)


if __name__ == "__main__":
    bench = bch.Bench("distance", distance)

    x = bch.FloatSweep(default=1, bounds=(1, 2))

    bench.plot_sweep("dis", input_vars=[x])

    bench.report.show()
