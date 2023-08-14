import holoviews as hv
import bencher as bch


class Investment(bch.ParametrizedSweep):
    inflation = bch.FloatSweep(default=8, bounds=[0.5, 15], units="%", samples=5)

    monthly_contribution = bch.FloatSweep(
        default=0,
        bounds=[0, 1000],
        units="$",
        samples=5,
        doc="The amount added to the investment each month",
    )

    interest = bch.FloatSweep(
        default=6.0,
        bounds=(0, 10),
        units="%",
        samples=5,
        doc="The amount of interest the investment returns (apr)",
    )

    tax_rate = bch.IntSweep(default=0, bounds=(0, 40), samples=2)
    period = bch.IntSweep(default=12, bounds=[0, 12], units="month")
    starting_value = bch.FloatSweep(default=1000, bounds=(0, 2000), units="$", samples=3)

    # RESULTS
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
        return self.get_results_values_as_dict(
            hv.Curve(values, self.param.period.as_dim(), self.param.portfolio_value.as_dim())
        )


if __name__ == "__main__":
    inv = Investment()

    bench = bch.Bench("Investment", inv.call, plot_lib=None)

    res = bench.plot_sweep(
        "Investment Sweep",
        description="This calculator lets you calculate the value of your investment over time",
        input_vars=[inv.param.monthly_contribution, inv.param.interest, inv.param.inflation],
        result_vars=[inv.param.portfolio_value],
    )

    bench.append(res.to_grid())
    bench.append(res.to(hv.Table).opts(width=1000))

    bench.append_tab(Investment().to_dynamic_map(name="Investment").opts())

    bench.show()
