import unittest
import bencher as bch


class ExSweep(bch.ParametrizedSweep):
    """A class containing all the sweep types, This class is used for unit testing how the configuration classes are serialised and hashed"""

    float1 = bch.FloatSweep(bounds=(0, 10), units="m/s")
    float2 = bch.FloatSweep(bounds=(0, 10), units="m/s")

    result = bch.ResultVar()

    def __call__(self, **kwargs) -> dict:
        self.update_params_from_kwargs(**kwargs)
        self.result = self.float1 + self.float2
        return self.get_results_values_as_dict()


class TestDataset(unittest.TestCase):
    def test_dataset_creation(self) -> None:
        bench = bch.Bench("test_dataset", ExSweep(),run_cfg=bch.BenchRunCfg(level=2))

        bench_cfg, _ = bench.setup_bench_cfg(
            "test_dataset", input_vars=[ExSweep.param.float1, ExSweep.param.float2]
        )
        bench_cfg, _ = bench.setup_dataset(bench_cfg)
        self.assertEqual(bench_cfg.ds,"")
        self.assertTupleEqual( bench_cfg.ds["result"].shape ,(2,2,1))

 