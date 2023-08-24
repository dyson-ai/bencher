from python_template.basic_class import BasicClass

from unittest import TestCase


class TestBasicClass(TestCase):
    def test_init(self):
        instance = BasicClass()

        self.assertEqual(instance.int_var, 0)
