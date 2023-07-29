import holoviews as hv
import panel as pn
from mortgage import Loan
import param
import bencher as bch


class Investment(bch.ParametrizedSweep):
    inflation = bch.FloatSweep(default=8, bounds=[0.5, 15], units="%", samples=5)
    monthly_contribution = bch.FloatSweep(default=0, bounds=[0, 1000], units="$", samples=5)
    interest = bch.FloatSweep(default=6.0, bounds=(0, 10), units="%", samples=5)
    tax_rate = bch.IntSweep(default=0, bounds=(0, 40), samples=2)
    period = bch.IntSweep(default=12, bounds=[1, 12], units="month")
    starting_value = bch.FloatSweep(default=1000, bounds=(0, 2000), samples=3)

    portfolio_value = bch.ResultVar(default=0, units="$")

    def call(self, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)
        self.portfolio_value = self.starting_value
        values = []
        for i in range(self.period):
            self.portfolio_value += self.monthly_contribution
            new_interest = self.portfolio_value * (self.interest / 100.0)
            self.portfolio_value += new_interest * (1 + self.tax_rate)
            self.portfolio_value *= 1 - (self.inflation / 100.0)
            values.append((i, self.portfolio_value))
        return self.get_results_values_as_dict(hv.Curve(values))


if __name__ == "__main__":
    pn.Row(Investment().to_dynamic_map()).show()
