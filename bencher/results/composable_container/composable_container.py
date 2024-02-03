from dataclasses import dataclass
import abc

from bencher.results.float_formatter import FormatFloat


# @dataclass


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
        self.container = None

    # def __init__(self) -> None:
    # pass

    # @abc.abstractmethod()
    def append(self, obj):
        pass

    def get_container(self):
        return self.container
