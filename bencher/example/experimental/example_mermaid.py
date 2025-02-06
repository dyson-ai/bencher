import param
import panel as pn
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

diagram.show()
