import unittest
import bencher as bch


class TestClassEnum(unittest.TestCase):
    def test_to_class(self):
        instance1 = bch.ExampleEnum.Class1.to_class()
        self.assertEqual(instance1.classname, "class1")
        instance2 = bch.ExampleEnum.Class2.to_class()
        self.assertEqual(instance2.classname, "class2")

    def test_to_class_from_enum(self):
        instance1 = bch.ExampleEnum.to_class_from_enum(bch.ExampleEnum.Class1)
        self.assertEqual(instance1.classname, "class1")
        instance2 = bch.ExampleEnum.to_class_from_enum(bch.ExampleEnum.Class2)
        self.assertEqual(instance2.classname, "class2")
