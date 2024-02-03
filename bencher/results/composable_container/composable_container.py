from enum import Enum, auto

from bencher.results.float_formatter import FormatFloat


class ComposeType(Enum):
    right = auto()
    down = auto()
    stack = auto()


class ComposableContainerBase:
    @staticmethod
    def label_formatter(var_name, var_value):
        if isinstance(var_value, (int, float)):
            var_value = FormatFloat()(var_value)
        if var_name is not None and var_value is not None:
            return f"{var_name}={var_value}"
        if var_name is not None:
            return f"{var_name}"
        if var_value is not None:
            return f"{var_value}"
        return None

    def __init__(self, horizontal: bool = True) -> None:
        self.horizontal: bool = horizontal
        self.compose_method = ComposeType.right
        self.container = None

    # def __init__(self) -> None:
    # pass

    # @abc.abstractmethod()
    def append(self, obj):
        pass
        # if method is None:
        # method = self.compose_method

    def get_container(self):
        return self.container
