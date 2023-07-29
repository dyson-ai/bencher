import holoviews as hv
import panel as pn
from mortgage import Loan
import param
import bencher as bch


class Mortgage(bch.ParametrizedSweep):
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

    def call(self, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)
        loan = Loan(
            principal=self.principal,
            interest=self.interest / 100,
            term=self.period,
        )

        # for i in range(self.period):

        installment = loan.schedule(self.installment_num)

        self.installment_payment = installment.payment
        self.installment_interest = installment.interest
        self.installment_total_interest = installment.total_interest
        self.installment_balance = installment.balance
        self.installment_principal = installment.principal

        return self.get_results_values_as_dict()


if __name__ == "__main__":
    mort = Mortgage()
    bench = bch.Bench("Mortgage", mort.call)

    bench.plot_sweep("mort", [mort.param.installment_num], [mort.param.installment_payment])

    bench.show()

    # pn.Row(Mortgage().to_dynamic_map()).show()
