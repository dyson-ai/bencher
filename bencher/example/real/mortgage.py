import math
import numpy as np
import bencher as bch
import param
from dataclasses import dataclass

from strenum import StrEnum
from enum import auto


class MortgateOffer(StrEnum):
    fixed2fee0 = auto()
    fixed2fee500 = auto()
    fixed2fee1000 = auto()


class Mort(bch.ParametrizedSweep):
    months = bch.IntSweep(bounds=[0, 360])


class MortResult(bch.ParametrizedSweep):
    debt = bch.ResultVar()


@dataclass
class Mortgage:
    principal: float
    intervals: int
    # current_debt: float
    interest_rate: float


def calc_deal(offer: Mort):
    m = Mortgage(18700, 30, 0.05)
    # m.intervals = 30
    # m.current_debt = 187000
    # m.interest_rate = 0.05

    mr = MortResult()
    for i in range(m.intervals):
        mr.append(compound_interest(m.principal, m.interest_rate, m.intervals, i))

    return mr


# https://www.calculatorsoup.com/calculators/financial/compound-interest-calculator.php
def compound_interest(principal, interest_rate, intervals, time, **kwargs):
    return principal * math.pow(1 + interest_rate / float(intervals), intervals * time)


# https://www.calculatorsoup.com/calculators/financial/compound-interest-calculator.php
def mortgage_payment(principal, interest_rate, intervals, time, **kwargs):
    return principal * math.pow(1 + interest_rate / float(intervals), intervals * time)


def ratesetter():
    bencher = bch.Bench("Mortgage", calc_deal, Mort)

    bencher.plot_sweep(
        "Time vs plan",
        input_vars=[Mort.param.years],
        result_vars=[
            MortResult.param.debt,
        ],
    )
    return bencher


if __name__ == "__main__":
    ratesetter().plot()
