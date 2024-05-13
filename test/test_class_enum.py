import unittest
import bencher as bch


class TestClassEnum(unittest.TestCase):
    def test_basic(self):
        instance1 = bch.ExampleEnum.to_class(bch.ExampleEnum.Class1)
        self.assertEqual(instance1.classname, "class1")
        instance2 = bch.ExampleEnum.to_class(bch.ExampleEnum.Class2)
        self.assertEqual(instance2.classname, "class2")
