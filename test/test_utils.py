import bencher as bch
import unittest
from bencher.utils import get_nearest_coords

import xarray as xr


class ExampleClass(bch.ParametrizedSweep):
    iv1 = bch.FloatSweep()
    rv1 = bch.ResultVar()


class TestBencherUtils(unittest.TestCase):
    def test_get_inputs(self) -> None:
        ex_instance = ExampleClass()
        inputs = ex_instance.get_inputs_only()

        print(inputs)

        self.assertEqual(len(inputs), 1)
        self.assertEqual(inputs[0].name, "iv1")

    def test_get_results(self) -> None:
        ex_instance = ExampleClass()
        results = ex_instance.get_results_only()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "rv1")

    def test_get_inputs_and_results(self) -> None:
        ex_instance = ExampleClass()
        inputs, results = ex_instance.get_input_and_results()

        self.assertEqual(len(inputs), 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(inputs["iv1"].name, "iv1")
        self.assertEqual(results["rv1"].name, "rv1")

    def test_get_results_values_as_dict(self) -> None:
        ex_instance = ExampleClass()

        ex_instance.rv1 = 3

        res = ex_instance.get_results_values_as_dict()

        self.assertEqual(res["rv1"], 3)

        # Tests that a named tuple with fields of different data types is created successfully

    def test_different_datatypes_namedtuple(self):
        result = bch.make_namedtuple("Test", field1=1, field2="value2", field3=True)
        self.assertEqual(result.field1, 1)
        self.assertEqual(result.field2, "value2")
        self.assertEqual(result.field3, True)

        # Tests that the function returns an empty tuple when an empty dictionary is passed as input

    def test_edge_case_empty_dictionary(self) -> None:
        input_dict = {}
        expected_output = ()
        self.assertEqual(bch.hmap_canonical_input(input_dict), expected_output)

    def test_dictionary_order(self) -> None:
        dic1 = {"x": 1, "y": 2}
        dic2 = {"y": 2, "x": 1}

        self.assertEqual(
            bch.hmap_canonical_input(dic1),
            bch.hmap_canonical_input(dic2),
        )

    # Tests that the function returns the nearest coordinate name value pair for a dataset containing multiple coordinates
    def test_multiple_coordinates(self):
        ds = xr.Dataset({"x": [1, 2, 3], "y": [4, 5, 6]})
        result = get_nearest_coords(ds, x=2.5, y=5.5)
        self.assertEqual(result, {"x": 3, "y": 6})
