from datetime import datetime
from typing import List

from pandas import Timestamp
from param import Selector
from bencher.variables.sweep_base import SweepBase, shared_slots


class TimeBase(SweepBase, Selector):
    """A class to capture a time snapshot of benchmark values.  Time is reprented as a continous value i.e a datetime which is converted into a np.datetime64.  To represent time as a discrete value use the TimeEvent class. The distinction is because holoview and plotly code makes different assumptions about discrete vs continous variables"""

    __slots__ = shared_slots

    def values(self, debug=False) -> List[str]:
        """return all the values for a parameter sweep.  If debug is true return a reduced list"""
        # print(self.sampling_str(debug))
        return self.objects


class TimeSnapshot(TimeBase):
    """A class to capture a time snapshot of benchmark values.  Time is reprented as a continous value i.e a datetime which is converted into a np.datetime64.  To represent time as a discrete value use the TimeEvent class. The distinction is because holoview and plotly code makes different assumptions about discrete vs continous variables"""

    __slots__ = shared_slots

    def __init__(
        self,
        datetime_src: datetime | str,
        units: str = "time",
        samples: int = None,
        samples_debug: int = 2,
        **params,
    ):
        if isinstance(datetime_src, str):
            TimeBase.__init__(self, [datetime_src], instantiate=True, **params)
        else:
            TimeBase.__init__(
                self,
                [Timestamp(datetime_src)],
                instantiate=True,
                **params,
            )
        self.units = units
        if samples is None:
            self.samples = len(self.objects)
        else:
            self.samples = samples
        self.samples_debug = min(self.samples, samples_debug)


class TimeEvent(TimeBase):
    """A class to represent a discrete event in time where the data was captured i.e a series of pull requests.  Here time is discrete and can't be interpolated, to represent time as a continous value use the TimeSnapshot class.  The distinction is because holoview and plotly code makes different assumptions about discrete vs continous variables"""

    __slots__ = shared_slots

    def __init__(
        self,
        time_event: str,
        units: str = "event",
        samples: int = None,
        samples_debug: int = 2,
        **params,
    ):
        TimeBase.__init__(
            self,
            [time_event],
            instantiate=True,
            **params,
        )
        self.units = units
        if samples is None:
            self.samples = len(self.objects)
        else:
            self.samples = samples
        self.samples_debug = min(self.samples, samples_debug)
