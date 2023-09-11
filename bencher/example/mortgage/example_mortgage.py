import holoviews as hv
from mortgage import Loan
import bencher as bch


class Mortgage(bch.ParametrizedSweep):
    inflation = bch.FloatSweep(default=8, bounds=[0.5, 15], units="%", samples=5)
    principal = bch.FloatSweep(default=200000, bounds=(0, 1000000), units="$")
    interest = bch.FloatSweep(default=6, bounds=(1, 10), samples=5, units="%")
    term = bch.IntSweep(default=24, bounds=(1, 24), units="months")

    period = bch.IntSweep(default=12, bounds=(1, 24), units="month")

    # RESULT VARS
    installment_payment = bch.ResultVar(units="$")
    installment_interest = bch.ResultVar(units="$")
    installment_total_interest = bch.ResultVar(units="$")
    installment_balance = bch.ResultVar(units="$")
    installment_principal = bch.ResultVar(units="$")

    def call(self, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)
        loan = Loan(
            principal=self.principal,
            interest=self.interest / 100,
            term=self.term,
        )

        mort_value = []
        for i in self.param.period.values():
            installment = loan.schedule(i)
            self.installment_payment = float(installment.payment)
            self.installment_interest = float(installment.interest)
            self.installment_total_interest = float(installment.total_interest)
            self.installment_balance = float(installment.balance)
            self.installment_principal = float(installment.principal)

            mort_value.append((i, self.installment_balance))

        pt = hv.Curve(
            mort_value, self.param.period.as_dim(), self.param.installment_balance.as_dim()
        )
        return self.get_results_values_as_dict(pt)


if __name__ == "__main__":
    mort = Mortgage()
    bench = bch.Bench("Mortgage", mort.call, plot_lib=None)

    res = bench.plot_sweep(
        "Mortgage",
        [mort.param.interest],
        [
            mort.param.installment_balance,
            mort.param.installment_principal,
        ],
    )

    bench.report.append(res.to_curve())

    bench.report.append(res.to(hv.Table).opts(width=1000))

    bench.report.append(res.to_holomap())

    bench.report.append(res.to_grid())

    bench.report.append_tab(mort.to_dynamic_map(name="Mortgage Calculator"))

    bench.show()
    # bench.plot()
