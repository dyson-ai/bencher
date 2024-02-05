import panel as pn
from bencher.results.composable_container.composable_container_base import ComposableContainerBase


class ComposableContainerPanel(ComposableContainerBase):
    def __init__(
        self,
        name: str = None,
        var_name: str = None,
        var_value: str = None,
        width: int = None,
        background_col: str = None,
        horizontal: bool = True,
    ) -> None:
        super().__init__(horizontal)

        container_args = {
            "name": name,
            "styles": {},
        }

        self.name = name

        if width is not None:
            container_args["styles"]["border-bottom"] = f"{width}px solid grey"
        if background_col is not None:
            container_args["styles"]["background"] = background_col

        if horizontal:
            self.container = pn.Column(**container_args)
            align = ("center", "center")
        else:
            self.container = pn.Row(**container_args)
            align = ("end", "center")

        label = self.label_formatter(var_name, var_value)
        if label is not None:
            self.label_len = len(label)
            side = pn.pane.Markdown(label, align=align)
            self.append(side)
