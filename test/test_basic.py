from unittest import TestCase
from python_template.basic_class import BasicClass


class TestBasicClass(TestCase):
    def test_init(self):
        instance = BasicClass()

        self.assertEqual(instance.int_var, 0)

    def test_init_fail(self):
        instance = BasicClass()

        self.assertEqual(instance.int_var, 1)
