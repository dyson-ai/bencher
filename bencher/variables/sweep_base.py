from typing import List, Any

import param
from param import Parameterized
import holoviews as hv
import panel as pn
from bencher.utils import hash_sha1

# slots that are shared across all Sweep classes
# param does not work with multiple inheritance so define here
shared_slots = ["units", "samples", "samples_debug"]


def hash_extra_vars(parameter: Parameterized) -> int:
    """hash extra meta vars in the parameter

    Args:
        parameter (Parameterized): a parameter

    Returns:
        int: hash
    """
    return hash_sha1((parameter.units, parameter.samples, parameter.samples_debug))


def describe_variable(v: Parameterized, debug: bool, include_samples: bool) -> List[str]:
    """Generate a string description of a variable

    Args:
        v (param.Parameterized): parameter to describe
        debug (bool): Generate a reduced number of samples from the variable
        include_samples (bool): Include a description of the samples

    Returns:
        str: String description of the variable
    """
    indent = "    "
    sampling_str = []
    sampling_str.append(f"{v.name}:")
    if include_samples:
        sampling_str.append(f"{indent}{v.sampling_str(debug)}")
    sampling_str.append(f"{indent}units: [{v.units}]")
    if v.doc is not None:
        sampling_str.append(f"{indent}docs: {v.doc}")
    for i in range(len(sampling_str)):
        sampling_str[i] = f"{indent}{sampling_str[i]}"
    return sampling_str


class SweepBase(param.Parameter):
    # def __init__(self, **params):
    # super().__init__(**params)
    # self.units = ""
    # slots = ["units", "samples", "samples_debug"]
    # __slots__ = shared_slots

    def values(self, debug: bool) -> List[Any]:
        """All sweep classes must implement this method. This generates sample values from based on the parameters bounds and sample number.

        Args:
            debug (bool): Return a reduced set of samples to enable fast debugging of a data generation and plotting pipeline. Ideally when debug is true, 2 samples will be returned

        Returns:
            List[Any]: A list of samples from the variable
        """
        raise NotImplementedError

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_extra_vars(self)

    def sampling_str(self, debug=False) -> str:
        """Generate a string representation of the of the sampling procedure

        Args:
            debug (bool): If true then self.samples_debug is used
        """

        samples = self.values(debug)
        object_str = ",".join([str(i) for i in samples])
        # return f"sampling {self.name} from: [{object_str}]"
        return f"sampling {self.name} from {object_str} in {len(samples)} samples"

    def as_slider(self, debug=False) -> pn.widgets.slider.DiscreteSlider:
        """given a sweep variable (self), return the range of values as a panel slider

        Args:
            debug (bool, optional): pass to the sweepvar to produce a full set of varaibles, or when debug=True, a reduces number of sweep vars. Defaults to False.

        Returns:
            pn.widgets.slider.DiscreteSlider: A panel slider with the values() of the sweep variable
        """
        return pn.widgets.slider.DiscreteSlider(name=self.name, options=list(self.values(debug)))

    def as_dim(self, compute_values=False, debug=False) -> hv.Dimension:
        """Takes a sweep variable and turns it into a holoview dimension

        Returns:
            hv.Dimension:
        """
        name_tuple = (self.name, self.name)
        if hasattr(self, "bounds"):
            if compute_values:
                return hv.Dimension(
                    name_tuple,
                    range=tuple(self.bounds),
                    unit=self.units,
                    values=self.values(debug),
                )

            return hv.Dimension(
                name_tuple,
                range=tuple(self.bounds),
                unit=self.units,
                default=self.default,
            )
        return hv.Dimension(
            name_tuple,
            unit=self.units,  # pylint: disable=no-member
            values=self.values(debug),
            default=self.default,
        )
