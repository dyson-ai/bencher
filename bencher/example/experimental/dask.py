class Counter:
    """A simple class to manage an incrementing counter"""

    n = 0

    def __init__(self):
        self.n = 0

    def increment(self):
        self.n += 1
        return self.n

    def add(self, x):
        self.n += x
        return self.n

import dask
from dask.distributed import Client
# from dask.distributed import Client  # Start a Dask Client

client = Client()

future = client.submit(Counter, actor=True)  # Create a Counter on a worker
counter = future.result()  # Get back a pointer to that object

counter
# <Actor: Counter, key=Counter-1234abcd>

future = counter.increment()  # Call remote method
future.result()  # Get back result
# 1

future = counter.add(10)  # Call remote method
future.result()  # Get back result
# 11
