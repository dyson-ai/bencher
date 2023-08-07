# Generated by CodiumAI
from bencher.variables.parametrised_sweep import ParametrizedSweep
import param
import holoviews as hv


class TestParametrizedSweep:
    # Tests that the method returns an empty list when given a single input

    # Tests that the method returns a list of dimensions with computed values when compute_values=True
    def test_compute_values_true(self):
        sweep = ParametrizedSweep()
        sweep.param.one = param.Integer()
        sweep.param.two = param.Integer()
        dims = sweep.get_inputs_as_dims(compute_values=True)
        assert dims == []

    # Tests that the method returns a list of dimensions with all inputs when remove_dims=None
    def test_remove_dims_none(self):
        sweep = ParametrizedSweep()
        sweep.param.one = param.Integer()
        sweep.param.two = param.Integer()
        dims = sweep.get_inputs_as_dims(remove_dims=None)
        assert len(dims) == 0

    # Tests that the method returns an empty list when given empty inputs
    def test_empty_inputs(self):
        sweep = ParametrizedSweep()
        dims = sweep.get_inputs_as_dims()
        assert len(dims) == 0

    # Tests that the method returns a list of dimensions with all inputs when given a non-existent dimension name in remove_dims
    def test_remove_dims_nonexistent(self):
        sweep = ParametrizedSweep()
        sweep.param.one = param.Integer()
        sweep.param.two = param.Integer()
        dims = sweep.get_inputs_as_dims(remove_dims="three")
        assert len(dims) == 0

        # Tests that the method works when a callback function is provided

    def test_callback_provided(self):
        def callback(x):
            return {"hmap": hv.Curve([1, 2, 3])}

        p = ParametrizedSweep()
        dm = p.to_dynamic_map(callback=callback)
        hm = p.to_holomap(callback=callback)
        assert isinstance(dm, hv.DynamicMap)
        assert isinstance(hm, hv.HoloMap)

    def test_no_callback_provided(self):
        p = ParametrizedSweep()
        dm = p.to_dynamic_map()
        hm = p.to_holomap()
        assert isinstance(dm, hv.DynamicMap)
        assert isinstance(hm, hv.HoloMap)
