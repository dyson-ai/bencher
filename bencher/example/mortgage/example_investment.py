import holoviews as hv
import bencher as bch


class Investment(bch.ParametrizedSweep):
    inflation = bch.FloatSweep(default=8, bounds=[0.5, 15], units="%", samples=5)
    monthly_contribution = bch.FloatSweep(default=0, bounds=[0, 1000], units="$", samples=5)
    interest = bch.FloatSweep(default=6.0, bounds=(0, 10), units="%", samples=5)
    tax_rate = bch.IntSweep(default=0, bounds=(0, 40), samples=2)
    period = bch.IntSweep(default=12, bounds=[1, 12], units="month")
    starting_value = bch.FloatSweep(default=1000, bounds=(0, 2000), samples=3)
    portfolio_value = bch.ResultVar(default=0, units="$")

    hmap = bch.ResultHmap()

    def __call__(self, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)
        self.portfolio_value = self.starting_value
        values = []
        for i in range(self.period):
            self.portfolio_value += self.monthly_contribution
            new_interest = self.portfolio_value * (self.interest / 100.0)
            self.portfolio_value += new_interest * (1 + self.tax_rate)
            self.portfolio_value *= 1 - (self.inflation / 100.0)
            values.append((i, self.portfolio_value))

        self.hmap = hv.Curve(
            values, self.param.period.as_dim(), self.param.portfolio_value.as_dim()
        )
        return self.get_results_values_as_dict()


if __name__ == "__main__":
    bench = bch.Bench("Investment", Investment(), plot_lib=None)

    res = bench.plot_sweep(
        "Investment Sweep",
        description="This calculator lets you calculate the value of your investment over time",
        input_vars=[
            Investment.param.monthly_contribution,
            Investment.param.interest,
            Investment.param.inflation,
        ],
        result_vars=[Investment.param.portfolio_value, Investment.param.hmap],
    )

    bench.report.append(res.to_grid())
    bench.report.append(res.to(hv.Table).opts(width=1000))

    bench.report.append_tab(Investment().to_dynamic_map(name="Investment"))

    bench.report.show()
