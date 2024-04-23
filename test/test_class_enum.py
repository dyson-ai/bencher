from future import __annotations__
import unittest
import bencher as bch
import random
from dataclasses import dataclass
from enum import auto


@dataclass
class BaseClass:
    baseclassname: str = "class0"


@dataclass
class Class1(BaseClass):
    classname: str = "class1"


@dataclass
class Class2(BaseClass):
    classname: str = "class2"


class ExampleEnum(bch.ClassEnum):

    Class1 = auto()
    Class2 = auto()

    @classmethod
    def to_class(cls, enum_val: ExampleEnum) -> BaseClass:
        return cls.to_class_generic("bencher.test.test_class_enum", enum_val)


class TestClassEnum(unittest.TestCase):
    def test_basic(self):

        instance1 = ExampleEnum.to_class(ExampleEnum.Class1)
        self.assertEqual(instance1.classname, "class1")
        instance2 = ExampleEnum.to_class(ExampleEnum.Class2)
        self.assertEqual(instance2.classname, "class2")
