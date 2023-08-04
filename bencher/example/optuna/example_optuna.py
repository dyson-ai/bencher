import bencher as bch
import numpy as np
import optuna
from optuna.samplers import TPESampler
from bencher.optuna_conversions import to_optuna


def objective(trial):
    x = trial.suggest_float("x", -10, 10)
    return x**2


study = optuna.create_study(sampler=TPESampler())
study.optimize(objective, n_trials=10)

rast_range = 1.5


class ToyOptimisationProblem(bch.ParametrizedSweep):
    input1 = bch.FloatSweep(default=0, bounds=[-rast_range, rast_range], samples=10)
    input2 = bch.FloatSweep(default=0, bounds=[-rast_range, rast_range], samples=10)
    offset = bch.FloatSweep(default=0, bounds=[-rast_range, rast_range])

    bump_scale = bch.FloatSweep(default=1.5, bounds=[1, 10])

    # RESULTS
    output = bch.ResultVar(bch.OptDir.minimize)

    def rastrigin(self, **kwargs) -> dict:
        """A modified version of the rastrigin function which is very difficult to find the global optimum
        https://en.wikipedia.org/wiki/Rastrigin_function

        Returns:
            dict: dictionary of return values
        """
        self.update_params_from_kwargs(**kwargs)
        x = np.array([self.input1 + 0.1234, self.input2 + 0.1234])

        self.output = (
            np.sum(x * x - self.bump_scale * np.cos(self.bump_scale * np.pi * x))
            + self.bump_scale * np.size(x)
            + self.offset
        )
        return self.get_results_values_as_dict()


def optuna_rastrigin():
    explorer = ToyOptimisationProblem()

    bench = bch.Bench("Rastrigin", explorer.rastrigin)

    res = bench.plot_sweep(
        "Rastrigin",
        input_vars=[explorer.param.input1, explorer.param.input2],
        result_vars=[explorer.param.output],
        # run_cfg=bch.BenchRunCfg(auto_plot=False),
    )

    optu = to_optuna(explorer.rastrigin, res, n_trials=100)
    print(optu)

    return bench


if __name__ == "__main__":
    optuna_rastrigin().show()
    # bench_rastrigin().show()
