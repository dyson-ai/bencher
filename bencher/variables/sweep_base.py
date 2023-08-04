from typing import List

import param
from param import Parameterized
import holoviews as hv
import panel as pn
from bencher.utils import hash_sha1

# slots that are shared across all Sweep classes
# param does not work with multiple inheritance so define here
shared_slots = ["units", "samples", "samples_debug"]


def sweep_hash(parameter: Parameterized) -> int:
    """Generate a hash for a sweep variable

    Returns:
        int: hash
    """
    curhash = 0
    for v in parameter.values():
        print(f"value:{v}, hash:{hash_sha1(v)}")
        curhash = hash_sha1((curhash, hash_sha1(v)))
    return curhash


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
    def values(self):
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

    def int_float_sampling_str(name, samples) -> str:
        """Generate a string representation of the of the sampling procedure

        Args:
            debug (bool): If true then self.samples_debug is used
        """

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
        if hasattr(self, "bounds"):
            if compute_values:
                return hv.Dimension(
                    (self.name, self.name),
                    range=tuple(self.bounds),
                    unit=self.units,
                    values=self.values(debug),
                )

            return hv.Dimension(
                (self.name, self.name),
                range=tuple(self.bounds),
                unit=self.units,
                default=self.default,
            )
        return hv.Dimension(
            (self.name, self.name),
            unit=self.units,
            values=self.values(debug),
            default=self.default,
        )
