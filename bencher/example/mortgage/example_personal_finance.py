import bencher as bch

from example_investment import Investment
from example_mortgage import Mortgage


class PersonalFinances(bch.ParametrizedSweep):
    inflation = bch.FloatSweep(default=8, bounds=[0.5, 15], units="%", samples=4)

    net_income = bch.FloatSweep(default=3000, bounds=(0, 5000))
    # savings = bch.FloatSweep(default=1000, bounds=(0, 3000))
    # mortgage_payment = bch.FloatSweep(default=1000, bounds=(500, 2000))

    # monthly_contribution = bch.FloatSweep(default=0, bounds=[0, 1000], units="$", samples=4)
    # investment_interest = bch.FloatSweep(default=6.0, bounds=(0.01, 10), units="%", samples=4)
    # tax_rate = bch.IntSweep(default=0, bounds=(0, 40), samples=2)
    # period = bch.IntSweep(default=12, bounds=[1, 12], units="month")
    # starting_value = bch.FloatSweep(default=1000, bounds=(0, 2000), samples=3)

    # discretionary_income = bch.FloatSweep(default=500, bounds=(0, 1000), units="$")
    # investment_to_mortgage_ratio = bch.FloatSweep(default=0.3, bounds=(0, 1), units="ratio")
    # investments_value = bch.ResultVar(default=0, units="$")

    # results
    net_wealth = bch.ResultVar(default=0, units="$")
    investments_value = bch.ResultVar(default=0, units="$")

    def call(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)

        inv = Investment(**kwargs)
        mort = Mortgage(**kwargs)

        pt = inv.plot_hmap()
        pt *= mort.plot_hmap()

        return self.get_results_values_as_dict(pt.opts(legend_position="right"))

        # # mort_inv = self.net_income - self.discretionary_income
        # # self.monthly_contribution = (
        # #     self.net_income
        # #     - self.discretionary_income
        # #     # - self.installment_payment
        # # )
        # # self.mortgage_payment
        # # self.monthly_contribution = (
        # #     self.post_tax_income * self.investment_to_mortgage_ratio
        # # )

        # for i in range(self.period):
        #     self.investments_value += self.monthly_contribution
        #     new_interest = self.investments_value * (self.investment_interest / 100.0)
        #     self.investments_value += new_interest * (1 + self.tax_rate)
        #     self.investments_value *= 1 - (self.inflation / 100.0)
        #     values.append((i, self.investments_value))

        # # self.calc_loan(**kwargs)

        # self.net_wealth + self.investments_value + self.installment_principal
        # print(values)
        # return self.get_results_values_as_dict(
        #     hv.Curve(values)
        #     # hv.Curve(values)
        # )


if __name__ == "__main__":
    pf = PersonalFinances()
    bench = bch.Bench("PersonalFinances", pf.call, plot_lib=None)

    # res = bench.plot_sweep(
    #     "Mortgage",
    #     [pf.param.interest],
    #     [
    #         pf.param.installment_balance,
    #         pf.param.installment_principal,
    #     ],
    # )

    # bench.report.append(res.to_curve())

    # bench.report.append(res.to(hv.Table).opts(width=1000))

    # bench.report.append(res.to_holomap())

    # bench.report.append(res.to_grid())

    bench.report.append_tab(pf.to_dynamic_map(name="Mortgage Calculator"))

    bench.report.show()
