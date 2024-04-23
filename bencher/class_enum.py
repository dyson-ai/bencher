from strenum import StrEnum
from typing import Any
import importlib
from abc import abstractmethod


class ClassEnum(StrEnum):
    """A ClassEnum is a pattern to make it easier to create factory a factory method that converts from an enum to a corresponding class.  Subclasses should implement to_class(enum_instance:EnumType) which takes an enum returns the corresponding instance of that class.  See test_class_enum.py for an example"""

    @classmethod
    def to_class_generic(cls, module_import: str, class_name: str) -> Any:
        """Create an instance of the class referred to by this enum

        Returns:
            Environment: instance of the environment pointed to by the class
        """

        class_def = getattr(importlib.import_module(module_import), class_name)
        return class_def()

    @classmethod
    @abstractmethod
    def to_class(cls) -> Any:
        """Subclasses should overrides this method to take  an enum returns the corresponding instance of that class."""
        raise NotImplementedError()
