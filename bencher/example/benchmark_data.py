"""This file contains an example of how to define benchmarking parameters sweeps. Categorical values are defined as enums and passed to EnumSweep classes, other types of sweeps are defined by their respective classes.

You can define a subclass which contains an input configuration which can be passed to a function in a type safe way. You can combine the subclass with a higher level class which contains more configuation parameters.  This is to help manage the complexity of large configuration/parameter spaces. 
"""

import math
import random
from enum import auto

from strenum import StrEnum

from bencher.bench_vars import (
    BoolSweep,
    EnumSweep,
    FloatSweep,
    IntSweep,
    OptDir,
    ParametrizedSweep,
    ResultVar,
    StringSweep,
)


class PostprocessFn(StrEnum):
    """Apply a postprocessing step to the data"""

    absolute = auto()  # return the abs of the output data
    negate = auto()  # return the negative of the output data


class NoiseDistribution(StrEnum):
    """A categorical variable describing the types of random noise"""

    uniform = auto()  # uniform random noiase
    gaussian = auto()  # gaussian noise
    lognorm = auto()  # lognorm noise


class NoiseCfg(ParametrizedSweep):
    """A class for storing the parameters for generating various types of noise"""

    noisy = BoolSweep(
        default=False, doc="Optionally add random noise to the output of the function"
    )

    noise_distribution = EnumSweep(NoiseDistribution, doc=NoiseDistribution.__doc__)

    sigma = FloatSweep(
        default=1,
        bounds=[0, 10],
        doc="The standard deviation of the noise",
        units="v",
    )


def calculate_noise(config: NoiseCfg) -> float:
    """Generate a float value based on a noise distribution and scale

    Args:
        config (NoiseCfg): see NoiseCfg type

    Returns:
        float: a noisy float value
    """

    noise = 0.0
    if config.noisy:
        match config.noise_distribution:
            case NoiseDistribution.uniform:
                noise = random.uniform(0, config.sigma)
            case NoiseDistribution.gaussian:
                noise = random.gauss(0, config.sigma)
            case NoiseDistribution.lognorm:
                noise = random.lognormvariate(0, config.sigma)

    return noise


class ExampleBenchCfgIn(NoiseCfg):
    """A class for representing a set of configuration options for the example worker. This class inherits from NoiseCfg so it also stores all its values as well."""

    theta = FloatSweep(default=0, bounds=[0, math.pi], doc="Input angle", units="rad", samples=30)
    offset = FloatSweep(default=0, bounds=[0, 0.3], doc="dc offset", units="v", samples=30)
    postprocess_fn = EnumSweep(PostprocessFn)


class ExampleBenchCfgOut(ParametrizedSweep):
    out_sin = ResultVar(units="v", direction=OptDir.minimize, doc="sin of theta with some noise")
    out_cos = ResultVar(units="v", direction=OptDir.minimize, doc="cos of theta with some noise")
    out_bool = ResultVar(units="%", doc="sin > 0.5")


def negate_fn(fn_input: float):
    """returns the negative of the input

    Args:
        fn_input (float): any float value

    Returns:
        float: negative of the input
    """
    return -fn_input


def bench_function(cfg: ExampleBenchCfgIn) -> ExampleBenchCfgOut:
    """Takes an ExampleBenchCfgIn and returns a ExampleBenchCfgOut output"""
    out = ExampleBenchCfgOut()
    noise = calculate_noise(cfg)

    postprocess_fn = abs if cfg.postprocess_fn == PostprocessFn.absolute else negate_fn

    out.out_sin = postprocess_fn(cfg.offset + math.sin(cfg.theta) + noise)
    out.out_cos = postprocess_fn(cfg.offset + math.cos(cfg.theta) + noise)

    out.out_bool = out.out_sin > 0.5
    return out


class AllSweepVars(ParametrizedSweep):
    """A class containing all the sweep types, This class is used for unit testing how the configuration classes are serialised and hashed"""

    var_float = FloatSweep(default=5, bounds=(0, 10), units="m/s")
    var_int = IntSweep(default=3, bounds=[0, 4])
    var_bool = BoolSweep()
    var_string = StringSweep(["string1", "string2"])
    var_enum = EnumSweep(PostprocessFn)
