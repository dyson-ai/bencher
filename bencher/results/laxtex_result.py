from __future__ import annotations
from typing import Optional
import panel as pn
from param import Parameter
import hvplot.pandas  # noqa pylint: disable=duplicate-code,unused-import
import xarray as xr

from panel.pane import LaTeX

pn.extension("mathjax")


def latex_text(var):
    var_str = str(var)
    return r"\text{" + var_str.replace("_", " ") + r"} \\"


def input_var_to_mermaid(iv):
    vs = "\n"
    if len(iv.values()) <= 5:
        vals = "\n".join([str(v) for v in iv.values()])
    else:
        v = iv.values()
        vals = [str(v[i]) for i in [0, 1, 0, -2, -1]]
        vals[2] = "⋮"
        vals = r"\\ ".join(vals)

    latex_str = r"""\begin{array}{c}"""
    # latex_str += fr"\text{iv.name}} \\"
    latex_str += latex_text(iv.name)
    latex_str += r"\left[ \begin{array}{c}"
    latex_str += f"{vals} "
    latex_str += r"\end{array} \right] \end{array}"
    return latex_str


def result_var_to_mermaid(self):
    latex_str = r"\begin{array}{c}"
    sizes = [str(len(i.values())) for i in self.input_vars]
    if len(sizes) == 1:
        sizes.insert(0, "1")
    sizes_str = r"\times".join(sizes)
    latex_str += " " + sizes_str + r"\\ "
    latex_str += r" \left[\begin{array}{cc}"

    for rv in self.result_vars:
        latex_str += " " + latex_text(rv.name) + " "
    latex_str += r"\end{array} \right]"
    latex_str += r"\end{array}"
    return latex_str


def to_latex(self) -> pn.pane.LaTeX:
    latex_str = r"\["
    if len(self.input_vars) > 0:
        for i, iv in enumerate(self.input_vars):
            latex_str += input_var_to_mermaid(iv)
            if i != len(self.input_vars) - 1:
                latex_str += r"\times"

        latex_str += r"\rightarrow\quad"
    latex_str += result_var_to_mermaid(self)
    latex_str += r"\]"

    # # vs +=""" -- "X" -- \n"""
    # for iv in self.result_vars:
    #     vs += result_var_to_mermaid(iv)
    # vs += "\nindex --> output"

    # # LaTeX representation of the vector and matrix
    # latex_str = r"""
    # \[
    # \begin{array}{c}
    # \text{Input} \\
    # \left[ \begin{array}{c} 1 \\ 2 \\ 3 \\ 4 \\ 5 \\ 6 \end{array} \right]
    # \end{array} \rightarrow\quad
    # \begin{array}{c}
    # 1\times6 \\
    # \left[ \begin{array}{cc} \text{result1} \\ \text{result2} \end{array} \right]
    # \end{array}
    # \]
    # """

    print(latex_str)

    return LaTeX(latex_str)
