import math
import numpy as np
import bencher as bch


class RateSetterCfg(bch.ParametrizedSweep):
    principal = bch.FloatSweep(
        default=1000, bounds=[0, 1000], units="£", doc="The starting investment"
    )
    intervals = bch.FloatSweep(
        default=365,
        bounds=[0, 365],
        units="days",
        doc="The number of intervals over which interest is calculated",
    )
    time = bch.FloatSweep(
        default=1, bounds=[0, 10], units="years", doc="The time to calculate interest over"
    )

    plan = bch.StringSweep(
        ["access", "plus", "max", "1 year"], doc="The available ratesetter plans"
    )

    penalty = bch.ResultVar()
    interest = bch.ResultVar()
    accrued = bch.ResultVar()
    effective_interest_rate = bch.ResultVar()


def ratesetter_plans(cfg: RateSetterCfg):
    output = {}

    accruedAccess = compound_interest(cfg.principal, 0.03, cfg.intervals, cfg.time)

    if cfg.plan == "access":
        penaltyDuration = 0
        interestRate = 0.03
    if cfg.plan == "plus":
        interestRate = 0.04
        penaltyDuration = 30.0 / 365
    if cfg.plan == "max":
        interestRate = 0.05
        penaltyDuration = 90.0 / 365

    if cfg.plan == "1 year":
        interestRate = 0.046
        penaltyDuration = 90.0 / 365

    if cfg.plan == "5 year":
        interestRate = 0.05
        penaltyDuration = 90.0 / 365

    accrued = compound_interest(cfg.principal, interestRate, cfg.intervals, cfg.time)
    penalty = compound_interest(accrued, interestRate, cfg.intervals, penaltyDuration) - accrued

    if cfg.plan == "1 year":
        penalty = accrued * 0.003

    if cfg.plan == "5 year":
        penalty = accrued * 0.003

    output["accrued"] = accrued - penalty
    output["interest"] = accrued - penalty - cfg.principal
    output["penalty"] = penalty
    if cfg.time == 0:
        output["effective_interest_rate"] = np.nan
    else:
        output["effective_interest_rate"] = (
            100.0 * math.log((accrued - penalty) / cfg.principal) / cfg.time
        )
    output["relToAc"] = output["interest"] - (accruedAccess - cfg.principal)
    return output


# https://www.calculatorsoup.com/calculators/financial/compound-interest-calculator.php
def compound_interest(principal, interestRate, intervals, time, **kwargs):
    return principal * math.pow(1 + interestRate / float(intervals), intervals * time)


def ratesetter():
    bencher = bch.Bench("ratesetter", ratesetter_plans, RateSetterCfg)

    bencher.plot_sweep(
        "Time vs plan",
        input_vars=[RateSetterCfg.param.time, RateSetterCfg.param.plan],
        result_vars=[
            RateSetterCfg.param.penalty,
            RateSetterCfg.param.accrued,
            RateSetterCfg.param.effective_interest_rate,
        ],
    )
    return bencher


if __name__ == "__main__":
    ratesetter().plot()
