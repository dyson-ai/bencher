import holoviews as hv
import panel as pn
from mortgage import Loan
import bencher as bch
from example_investment import Investment


class EconomicClimate(bch.ParametrizedSweep):
    inflation = bch.FloatSweep(default=8, bounds=[0.5, 15], units="%", samples=5)


class Mortgage(EconomicClimate):
    # INPUTS
    inflation = bch.FloatSweep(default=8, bounds=[0.5, 15], units="%", samples=5)

    principal = bch.FloatSweep(default=200000, bounds=(0, 1000000), units="$")
    interest = bch.FloatSweep(default=6, bounds=(1, 10), samples=5, units="%")
    period = bch.IntSweep(default=24, bounds=(1, 30 * 12), units="months")

    installment_num = bch.IntSweep(default=1, bounds=(1, 24), units="month")

    # RESULT VARS
    installment_payment = bch.ResultVar(units="$")
    installment_interest = bch.ResultVar(units="$")
    installment_total_interest = bch.ResultVar(units="$")
    installment_balance = bch.ResultVar(units="$")
    installment_principal = bch.ResultVar(units="$")

    def calc_loan(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)
        loan = Loan(
            principal=self.principal,
            interest=self.interest / 100,
            term=self.period,
        )

        installment = loan.schedule(self.installment_num)

        self.installment_payment = installment.payment
        self.installment_interest = installment.interest
        self.installment_total_interest = installment.total_interest
        self.installment_balance = installment.balance
        self.installment_principal = installment.principal

        return self.get_results_values_as_dict()

    def call(self, **kwargs):
        return self.calc_loan(**kwargs)


# res = bench.plot_sweep(
#     "Mortage",
#     input_vars=[mort_sim.param.installment_num],
#     result_vars=[
#         mort_sim.param.installment_payment,
#         mort_sim.param.installment_interest,
#         mort_sim.param.installment_total_interest,
#         mort_sim.param.installment_balance,
#         mort_sim.param.installment_principal,
#     ],
#     plot_lib=bch.PlotLibrary.none(),
# )

# res = bench.plot_sweep(
#     "Mortage vs Interest Rates",
#     input_vars=[mort_sim.param.installment_num, mort_sim.param.interest],
#     result_vars=[
#         # mort_sim.param.installment_payment,
#         # mort_sim.param.installment_interest,
#         mort_sim.param.installment_total_interest,
#         mort_sim.param.installment_balance,
#         mort_sim.param.installment_principal,
#     ],
# )


class PersonalFinances(Mortgage):
    inflation = bch.FloatSweep(default=8, bounds=[0.5, 15], units="%", samples=4)

    net_income = bch.FloatSweep(default=3000, bounds=(0, 5000))
    savings = bch.FloatSweep(default=1000, bounds=(0, 3000))
    mortgage_payment = bch.FloatSweep(default=1000, bounds=(500, 2000))

    monthly_contribution = bch.FloatSweep(default=0, bounds=[0, 1000], units="$", samples=4)
    investment_interest = bch.FloatSweep(default=6.0, bounds=(0.01, 10), units="%", samples=4)
    tax_rate = bch.IntSweep(default=0, bounds=(0, 40), samples=2)
    period = bch.IntSweep(default=12, bounds=[1, 12], units="month")
    starting_value = bch.FloatSweep(default=1000, bounds=(0, 2000), samples=3)

    discretionary_income = bch.FloatSweep(default=500, bounds=(0, 1000), units="$")
    investment_to_mortgage_ratio = bch.FloatSweep(default=0.3, bounds=(0, 1), units="ratio")
    investments_value = bch.ResultVar(default=0, units="$")

    # results
    net_wealth = bch.ResultVar(default=0, units="$")
    investments_value = bch.ResultVar(default=0, units="$")

    def call(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)

        loan = Loan(
            principal=self.principal,
            interest=self.investment_interest / 100,
            term=self.period,
        )

        installment = loan.schedule(self.installment_num)

        self.installment_payment = installment.payment
        self.installment_interest = installment.interest
        self.installment_total_interest = installment.total_interest
        self.installment_balance = installment.balance
        self.installment_principal = float(installment.principal)

        # print(self.installment_payment)
        self.investments_value = self.starting_value
        values = []

        # mort_inv = self.net_income - self.discretionary_income
        # self.monthly_contribution = (
        #     self.net_income
        #     - self.discretionary_income
        #     # - self.installment_payment
        # )
        # self.mortgage_payment
        # self.monthly_contribution = (
        #     self.post_tax_income * self.investment_to_mortgage_ratio
        # )

        for i in range(self.period):
            self.investments_value += self.monthly_contribution
            new_interest = self.investments_value * (self.investment_interest / 100.0)
            self.investments_value += new_interest * (1 + self.tax_rate)
            self.investments_value *= 1 - (self.inflation / 100.0)
            values.append((i, self.investments_value))

        # self.calc_loan(**kwargs)

        self.net_wealth = self.investments_value + self.installment_principal
        print(values)
        return self.get_results_values_as_dict(
            hv.Curve(values)
            # hv.Curve(values)
        )

    def call_vec(self, **kwargs):
        return self.call(**kwargs)


mort_sim = Mortgage()
inv = Investment()
pf = PersonalFinances()

bench = bch.Bench("Mortgage", mort_sim.calc_loan)


pn.Row(inv.to_dynamic_map()).show()


bench.plot_sweep("lol")

bench.worker = inv.__call__

res = bench.plot_sweep(
    title="Investment Calculator",
    description="This calculator lets you calculate the value of your investment over time",
    input_vars=[
        # inv.param.period,
        inv.param.interest,
        inv.param.monthly_contribution,
        inv.param.inflation,
    ],
    # const_vars=[(inv.param.interest, .06)],
    result_vars=[inv.param.portfolio_value],
    # plot_lib=bch.PlotLibrary.default().add(bch.PlotTypes.lineplot_hv),
)

bench.report.append(res.to_grid())
# grid(["inflation", "monthly_contribution"]))
bench.report.append_tab(inv.to_dynamic_map())

# bench.report.append_tab(inv.to_holomap(inv.call).layout(kdims=["inflation"]))


# bench.report.append_tab(pf.to_dynamic_map(pf.call_vec))

bench.report.show()

# bench.worker = inv.call
bench.worker = pf.call

res = bench.plot_sweep(
    title="Mortgage Simulator",
    description="This calculator lets you calculate the value of your investment over time",
    input_vars=[
        pf.param.period,
        pf.param.investment_interest,
        inv.param.monthly_contribution,
        inv.param.inflation,
    ],
    # const_vars=[(inv.param.interest, .06)],
    result_vars=[pf.param.investments_value],
    # plot_lib=bch.PlotLibrary.default().add(bch.PlotTypes.lineplot_hv),
    plot_lib=bch.PlotLibrary.none(),
)

# bench.report.append(res.to_grid().overlay("month"))

bench.report.append(res.to_curve().grid(["inflation", "monthly_contribution"]).opts())


# res = bench.plot_sweep(
#     title="Investment Calculator",
#     description="This calculator lets you calculate the value of your investment over time",
#     input_vars=[
#         inv.param.period,
#         # inv.param.interest,
#         # inv.param.monthly_contribution,
#         # inv.param.inflation,
#     ],
#     # const_vars=[(inv.param.interest, .06)],
#     result_vars=[inv.param.portfolio_value],
#     # plot_lib=bch.PlotLibrary.default().add(bch.PlotTypes.lineplot_hv),
# )


# print(inv.get_inputs_as_dims())

# bench.plots_instance.append(
#     hv.DynamicMap(callback=inv.plot, kdims=inv.get_inputs_as_dims()).opts(
#         width=1000, height=1000
#     )
# )


# bench.plots_instance.append(
#     hv.DynamicMap(Investment(), Investment().param.get_inputs_as_dims(True))
# ).opts(width=1000, height=1000)

# bench.report.append(res.to_curve().opts(width=1000, height=1000))


# bench.report.append(res.to_curve().grid(["inflation", "monthly_contribution"]).opts())


# bench.

# bench.report.append(res.to_curve().grid())
# bench.report.append(res.to_grid())


# ds = hv.Dataset(res.ds)
# # pt = ds.to(hv.Curve,vdims=vdims)

# bench.report.append(
#     ds.to(
#         hv.Curve, vdims=["installment_balance", "installment_total_interest"]
#     ).layout("interest")
# )

# bench.report.append(
#     ds.to(hv.Curve, vdims=["installment_total_interest"]).layout("interest")
# )

# bench.report.append(
#     ds.to(hv.Curve, vdims=["installment_total_interest"]).overlay("interest")
# )

# bench.report.append(res.to_curve(vdims=["installment_balance"]).overlay("interest"))

# bench.plots_instance.append(res.to_nd_layout())

bench.report.show()
