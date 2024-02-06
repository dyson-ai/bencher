from enum import Enum, auto
from typing import Any
from bencher.results.float_formatter import FormatFloat


# TODO enable these options
class ComposeType(Enum):
    right = auto()  # append the container to the right (creates a row)
    down = auto()  # append the container below (creates a column)
    overlay = auto()  # overlay on top of the current container (alpha blending)
    sequence = auto()  # display the container after (in time)

    def flip(self):
        match self:
            case ComposeType.right:
                return ComposeType.down
            case ComposeType.down:
                return ComposeType.right
            case _:
                raise RuntimeError("cannot flip this type")

    @staticmethod
    def from_horizontal(horizontal: bool):
        if horizontal:
            return ComposeType.right
        return ComposeType.down


class ComposableContainerBase:
    """A base class for renderer backends.  A composable renderer"""

    def __init__(
        self, horizontal: bool = True, compose_method: ComposeType = ComposeType.right
    ) -> None:
        self.horizontal: bool = horizontal
        self.compose_method = compose_method
        self.container = []

    @staticmethod
    def label_formatter(var_name: str, var_value: int | float | str) -> str:
        """Take a variable name and values and return a pretty version with approximate fixed width

        Args:
            var_name (str): The name of the variable, usually a dimension
            var_value (int | float | str): The value of the dimension

        Returns:
            str: Pretty string representation with fixed width
        """

        if isinstance(var_value, (int, float)):
            var_value = FormatFloat()(var_value)
        if var_name is not None and var_value is not None:
            return f"{var_name}={var_value}"
        if var_name is not None:
            return f"{var_name}"
        if var_value is not None:
            return f"{var_value}"
        return None

    def append(self, obj: Any) -> None:
        """Add an object to the container.  The relationship between the objects is defined by the ComposeType

        Args:
            obj (Any): Object to add to the container
        """
        self.container.append(obj)

    def render(self):
        """Return a representation of the container that can be composed with other render() results. This function can also be used to defer layout and rending options until all the information about the container content is known.  You may need to ovverride this method depending on the container. See composable_container_video as an example.

        Returns:
            Any: Visual representation of the container that can be combined with other containers
        """
        return self.container
