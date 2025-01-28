import nbformat as nbf
from typing import Any
import bencher as bch
import numpy as np

from enum import auto
from strenum import StrEnum
import random
import holoviews as hv
import math
from pathlib import Path

from bencher.example.meta.example_meta import BenchableObject


class BenchMetaGen(bch.ParametrizedSweep):
    """This class uses bencher to display the multidimensional types bencher can represent"""

    float_vars = bch.IntSweep(
        default=0, bounds=(0, 4), doc="The number of floating point variables that are swept"
    )
    categorical_vars = bch.IntSweep(
        default=0, bounds=(0, 3), doc="The number of categorical variables that are swept"
    )
    sample_with_repeats = bch.IntSweep(default=1, bounds=(1, 10))

    sample_over_time = bch.BoolSweep(default=False)

    level = bch.IntSweep(default=2, units="level", bounds=(2, 5))

    plots = bch.ResultReference(units="int")

    def __call__(self, **kwargs: Any) -> Any:
        self.update_params_from_kwargs(**kwargs)

        run_cfg = bch.BenchRunCfg()
        run_cfg.level = self.level
        run_cfg.repeats = self.sample_with_repeats
        run_cfg.over_time = self.sample_over_time
        run_cfg.plot_size = 500

        bench = bch.Bench("benchable", BenchableObject(), run_cfg=run_cfg)

        inputs_vars_float = [
            "float1",
            "float2",
            "float3",
            "sigma",
        ]

        inputs_vars_cat = [
            "noisy",
            "noise_distribution",
            "negate_output",
        ]

        input_vars = (
            inputs_vars_float[0 : self.float_vars] + inputs_vars_cat[0 : self.categorical_vars]
        )

        print(input_vars)
        print("inputsfjkdfjslkjf", input_vars)

        inputs_str = str(input_vars)

        res = bench.plot_sweep(
            "test",
            input_vars=input_vars,
            result_vars=[BenchableObject.param.distance],
            # result_vars=[BenchableObject.param.distance, BenchableObject.param.sample_noise],
            # result_vars=[ BenchableObject.param.sample_noise],
            # result_vars=[BenchableObject.param.result_hmap],
            plot_callbacks=False,
        )

        title = res.to_plot_title()

        title = f"{len(input_vars)}_in"

        nb = nbf.v4.new_notebook()
        text = f"""# {title}"""

        code = f"""

import bencher as bch
from bencher.example.meta.example_meta import BenchMeta

bench = BenchMeta().to_bench(bch.BenchRunCfg())
bench.plot_sweep(input_vars={input_vars}, const_vars=dict(float_vars=2,level=5))
bench.report.show()
"""

        nb["cells"] = [nbf.v4.new_markdown_cell(text), nbf.v4.new_code_cell(code)]
        fname = "test.ipynb"

        # print(Path())
        with open(fname, "w") as f:
            # nbf.write(nb, f"ex_{title.replace(" ","_")}.ipynb")
            nbf.write(nb, f"docs/reference/meta/ex_{title}.ipynb")

        self.plots = bch.ResultReference()
        self.plots.obj = res.to_auto()
        return super().__call__()


def example_meta(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    bench = BenchMetaGen().to_bench(run_cfg, report)

    bench.plot_sweep(
        title="Meta Bench",
        description="""## All Combinations of Variable Sweeps and Resulting Plots
This uses bencher to display all the combinations of plots bencher is able to produce""",
        input_vars=[
            # bch.p("float_vars", [0, 1, 2, 3]),
            bch.p("float_vars", [0, 1]),
            # BenchMetaGen.param.categorical_vars,
            # bch.p("sample_with_repeats", [1, 2]),
            # BenchMeta.param.sample_over_time,
        ],
        const_vars=[
            # BenchMeta.param.float_vars.with_const(1),
            # BenchMeta.param.sample_with_repeats.with_const(2),
            # BenchMeta.param.categorical_vars.with_const(2),
            # BenchMeta.param.sample_over_time.with_const(True),
        ],
    )

    return bench


if __name__ == "__main__":
    example_meta().report.show()
