import math
import numpy as np
from dataclasses import dataclass


@dataclass
class V3:
    x: float
    y: float
    z: float
    distance: float

    def __call__(self):
        self.distance = math.pow(np.linalg.norm(np.array([self.x, self.y, self.z])), 2)


def distance(x, y, z):
    return math.pow(np.linalg.norm(np.array([x, y, z])), 2)
