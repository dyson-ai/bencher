from __future__ import annotations
import panel as pn
from panel.pane import LaTeX
from typing import Optional

pn.extension("mathjax")


def latex_text(var):
    var_str = str(var)
    return r"\text{" + var_str.replace("_", " ") + r"} \\"


def input_var_to_mermaid(input_var):
    vs = "\n"
    if len(input_var.values()) <= 5:
        vals = "\n".join([str(v) for v in input_var.values()])
    else:
        v = input_var.values()
        vals = [str(v[i]) for i in [0, 1, 0, -2, -1]]
        vals[2] = "⋮"
        vals = r"\\ ".join(vals)

    latex_str = r"""\begin{array}{c}"""
    # latex_str += fr"\text{iv.name}} \\"
    latex_str += latex_text(input_var.name)
    latex_str += r"\left[ \begin{array}{c}"
    latex_str += vals + " "
    latex_str += r"\end{array} \right] \end{array}"
    return latex_str


def result_var_to_mermaid(bench_cfg):
    latex_str = r"\begin{array}{c}"
    sizes = [str(len(i.values())) for i in bench_cfg.input_vars]
    if len(sizes) == 1:
        sizes.insert(0, "1")
    sizes_str = r"\times".join(sizes)
    latex_str += sizes_str + r"\\ "
    latex_str += r" \left[\begin{array}{cc}"

    for rv in bench_cfg.result_vars:
        latex_str +=  latex_text(rv.name)  
    latex_str += r"\end{array} \right]"
    latex_str += r"\end{array}"
    return latex_str


def to_latex(bench_cfg) -> Optional[pn.pane.LaTeX]:
    if len(bench_cfg.input_vars) > 0:
        latex_str = r"\["
        for i, iv in enumerate(bench_cfg.input_vars):
            latex_str += input_var_to_mermaid(iv)
            if i != len(bench_cfg.input_vars) - 1:
                latex_str += r"\times"

        latex_str += r"\rightarrow\quad"
        latex_str += result_var_to_mermaid(bench_cfg)
        latex_str += r"\]"
        return LaTeX(latex_str)
    return None
