import bencher as bch
import unittest


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
