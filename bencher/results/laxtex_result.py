from __future__ import annotations
import panel as pn
from panel.pane import LaTeX
from typing import Optional

pn.extension("mathjax")


def latex_text(var):
    var_str = str(var)
    return r"\text{" + var_str.replace("_", " ") + r"} \\"


def input_var_to_latex(input_var):
    vals = input_var.values()
    displayed_vals = vals
    if len(vals) > 5:
        displayed_vals = [vals[i] for i in [0, 1, 0, -2, -1]]
        displayed_vals[2] = "⋮"
    v = r"\\ ".join([str(va) for va in displayed_vals])

    print(v)
    latex_str = r"""\begin{array}{c}"""
    latex_str += latex_text(input_var.name)
    latex_str += f"{len(vals)}" + r"\times1 \\"
    latex_str += r"\left[ \begin{array}{c}"
    latex_str += f"{v} "
    latex_str += r"\end{array} \right] \end{array}"
    return latex_str


def result_var_to_latex(bench_cfg):
    latex_str = r"\begin{array}{c}"
    sizes = [str(len(i.values())) for i in bench_cfg.input_vars]
    if len(sizes) == 1:
        sizes.insert(0, "1")
    sizes_str = r"\times".join(reversed(sizes))
    latex_str += sizes_str + r"\\ "
    latex_str += r" \left[\begin{array}{cc}"

    for rv in bench_cfg.result_vars:
        latex_str += latex_text(rv.name)
    latex_str += r"\end{array} \right]"
    latex_str += r"\end{array}"
    return latex_str


def to_latex(bench_cfg) -> Optional[pn.pane.LaTeX]:
    if len(bench_cfg.input_vars) > 0:
        latex_str = r"\["
        for i, iv in enumerate(bench_cfg.input_vars):
            latex_str += input_var_to_latex(iv)
            if i != len(bench_cfg.input_vars) - 1:
                latex_str += r"\times"

        latex_str += r"\rightarrow\quad"
        latex_str += result_var_to_latex(bench_cfg)
        latex_str += r"\]"
        return LaTeX(latex_str)
    return None
