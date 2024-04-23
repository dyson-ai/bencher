from __future__ import annotations
from strenum import StrEnum
from typing import Any
import importlib
from abc import abstractmethod
from dataclasses import dataclass
from enum import auto


class ClassEnum(StrEnum):
    """A ClassEnum is a pattern to make it easier to create factory a factory method that converts from an enum to a corresponding class.  Subclasses should implement to_class(enum_instance:EnumType) which takes an enum returns the corresponding instance of that class."""

    @classmethod
    def to_class_generic(cls, module_import: str, class_name: str) -> Any:
        """Create an instance of the class referred to by this enum

        Returns:
            Any: instance of the class
        """

        class_def = getattr(importlib.import_module(module_import), class_name)
        return class_def()

    @classmethod
    @abstractmethod
    def to_class(cls, enum_val: ClassEnum) -> Any:
        """Subclasses should overrides this method to take  an enum returns the corresponding instance of that class."""
        raise NotImplementedError()


@dataclass
class BaseClass:
    baseclassname: str = "class0"


@dataclass
class Class1(BaseClass):
    classname: str = "class1"


@dataclass
class Class2(BaseClass):
    classname: str = "class2"


class ExampleEnum(ClassEnum):
    Class1 = auto()
    Class2 = auto()

    @classmethod
    def to_class(cls, enum_val: ExampleEnum) -> BaseClass:
        return cls.to_class_generic("bencher.class_enum", enum_val)
