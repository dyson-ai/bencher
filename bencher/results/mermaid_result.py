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


class MermaidResult(PanelResult):
    def to_block_summary(self, result_var: Parameter = None, **kwargs) -> Optional[pn.pane.Pane]:
        # benchmark_sampling_str.append("Input Variables:")

        def procs(id1, title, contents):
            return f"\t{id1}" + "@{ shape: procs, label: " + f'**{title}**\n{contents}"' + "}"

        vs = "floatchar LR\n"
        input_str = ""
        for iv in self.bench_cfg.input_vars:
            vs += procs("A", iv.name, "\n".join([str(v) for v in iv.values()]))
            # input_str += " " + iv.name

        vs += """ -- "X" --> """

        input_str = ""
        for iv in self.bench_cfg.input_vars:
            vs += procs("B", iv.name, "\n".join([str(v) for v in iv.values()]))

        print(vs)
        # if self.const_vars and (self.summarise_constant_inputs):
        #     benchmark_sampling_str.append("\nConstants:")
        #     for cv in self.const_vars:
        #         benchmark_sampling_str.extend(describe_variable(cv[0], False, cv[1]))

        # benchmark_sampling_str.append("\nResult Variables:")
        # for rv in self.result_vars:
        #     benchmark_sampling_str.extend(describe_variable(rv, False))

        diagram = MermaidDiagram(
            value=(
                f"""
        graph LR
            {input_str} --- B
            B-->C[fa:fa-ban forbidden]
            B-->D(fa:fa-spinner);
                """
            )
        )

        v2 = """
        flowchart LR
            A@{ shape: procs, label: "**Input1** \n1\n2\n...\n5\n6"} -- "X" --> B@{shape: procs, label: "**Input2** \nalpha\nbeta\n...\nzeta"}
                 """

        print(v2)

        diagram = MermaidDiagram(value=v2)
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
