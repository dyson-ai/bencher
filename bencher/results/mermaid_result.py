from __future__ import annotations
from typing import Optional
import panel as pn
from param import Parameter
import hvplot.xarray  # noqa pylint: disable=duplicate-code,unused-import
import hvplot.pandas  # noqa pylint: disable=duplicate-code,unused-import
import xarray as xr

from bencher.results.panel_result import PanelResult
from bencher.results.bench_result_base import ReduceType

from bencher.plotting.plot_filter import VarRange
from bencher.variables.results import ResultVar

import param
from panel.custom import JSComponent

pn.extension()


class MermaidDiagram(JSComponent):
    value = param.String(default="graph TD; A-->B; A-->C; B-->D; C-->D;")

    _esm = """
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';

    mermaid.initialize({ startOnLoad: false });

    export async function render({ model, el }) {
      const { svg } = await mermaid.render('graphDiv', model.value);
      el.innerHTML = svg; // Set the rendered SVG in the container
    }
    """

    _importmap = {
        "imports": {"mermaid": "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"}
    }


diagram = MermaidDiagram(
    value=(
        """
        graph LR
            A --- B
            B-->C[fa:fa-ban forbidden]
            B-->D(fa:fa-spinner);
        """
    )
)


def input_var_to_mermaid(iv):
    vs = "\n"
    if len(iv.values()) <= 5:
        vals = "\n".join([str(v) for v in iv.values()])
    else:
        v = iv.values()
        vals = [str(v[i]) for i in [0, 1, 0, -2, -1]]
        vals[2] = "⋮"
        vals = "\n".join(vals)

    vs += f"""\t{iv.name}["<u>**{iv.name}**</u> \n{vals}"]"""
    return vs


def procs(id1, title, contents):
    return f"\t{id1}" + "@{ shape: procs, label: " + f'**{title}**\n{contents}"' + "}"


def result_var_to_mermaid(rv):
    vs = "\n"
    vs += f"""\t{rv.name}["**{rv.name} ({rv.units})**"]"""
    return vs


class MermaidResult(PanelResult):
    def to_block_summary(self, result_var: Parameter = None, **kwargs) -> Optional[pn.pane.Pane]:
        vs = "flowchart LR"
        for iv in self.bench_cfg.input_vars:
            vs += input_var_to_mermaid(iv)

        # vs +=""" -- "X" -- \n"""
        for iv in self.bench_cfg.result_vars:
            vs += result_var_to_mermaid(iv)
        vs += "\nindex --> output"

        print(vs)
        # benchmark_sampling_str.append("\nResult Variables:")
        # for rv in self.result_vars:
        #     benchmark_sampling_str.extend(describe_variable(rv, False))

        #         diagram = MermaidDiagram(
        #             value=(
        #                 f"""
        #         graph LR
        #             {input_str} --- B
        #             B-->C[fa:fa-ban forbidden]
        #             B-->D(fa:fa-spinner);
        #                 """
        #             )
        #         )
        #         v2 = """
        # flowchart LR
        #     A@{ shape: procs, label: "**Input1** \n1\n2\n...\n5\n6"} -- "X" --> B@{shape: procs, label: "**Input2** \nalpha\nbeta\n...\nzeta"}
        #                  """

        #         print(v2)

        diagram = MermaidDiagram(value=vs)
        # diagram2 = MermaidDiagram(value=v)

        # diagram = MermaidDiagram(
        #     value=(
        #         """
        #         flowchart LR
        #             A@{ shape: procs, label: "**Input1**\n1\n2\n...\n5\n6" } -- "X" --> B@{ shape: procs, label: "**Input2**\nalpha\nbeta\n...\nzeta" }
        #         """
        #     )
        # )
        return diagram
