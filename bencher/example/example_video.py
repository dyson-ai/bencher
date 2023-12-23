import bencher as bch
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import ArtistAnimation


# code from https://ipython-books.github.io/124-simulating-a-partial-differential-equation-reaction-diffusion-systems-and-turing-patterns/
class TuringPattern(bch.ParametrizedSweep):
    alpha = bch.FloatSweep(default=2.8e-4, bounds=(2e-4, 5e-3))
    beta = bch.FloatSweep(default=5e-3, bounds=(1e-3, 9e-3))
    tau = bch.FloatSweep(default=0.1, bounds=(0.01, 0.5))
    k = bch.FloatSweep(default=-0.005, bounds=(-0.01, 0.01))

    size = bch.IntSweep(default=50, bounds=(30, 200), doc="size of the 2D grid")
    time = bch.FloatSweep(default=20.0, bounds=(1, 100), doc="total time of simulation")
    dt = bch.FloatSweep(default=0.001, doc="simulation time step")

    # video = bch.ResultContainer()
    video = bch.ResultVideo()
    # video = bch.ResultContainer()

    def laplacian(self, Z, dx):
        Ztop = Z[0:-2, 1:-1]
        Zleft = Z[1:-1, 0:-2]
        Zbottom = Z[2:, 1:-1]
        Zright = Z[1:-1, 2:]
        Zcenter = Z[1:-1, 1:-1]
        return (Ztop + Zleft + Zbottom + Zright - 4 * Zcenter) / dx**2

    def update(self, U, V, dx):
        # We compute the Laplacian of u and v.
        deltaU = self.laplacian(U, dx)
        deltaV = self.laplacian(V, dx)
        # We take the values of u and v inside the grid.
        Uc = U[1:-1, 1:-1]
        Vc = V[1:-1, 1:-1]
        # We update the variables.
        U[1:-1, 1:-1], V[1:-1, 1:-1] = (
            Uc + self.dt * (self.alpha * deltaU + Uc - Uc**3 - Vc + self.k),
            Vc + self.dt * (self.beta * deltaV + Uc - Vc) / self.tau,
        )
        # Neumann conditions: derivatives at the edges
        # are null.
        for Z in (U, V):
            Z[0, :] = Z[1, :]
            Z[-1, :] = Z[-2, :]
            Z[:, 0] = Z[:, 1]
            Z[:, -1] = Z[:, -2]

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)

        n = int(self.time / self.dt)  # number of iterations
        dx = 2.0 / self.size  # space step

        U = np.random.rand(self.size, self.size)
        V = np.random.rand(self.size, self.size)

        fig, ax = plt.subplots(frameon=False, figsize=(2, 2))
        fig.set_tight_layout(True)
        ax.set_axis_off()

        artists = []

        for i in range(n):
            self.update(U, V, dx)
            if i % 500 == 0:
                artists.append([ax.imshow(U)])

        ani = ArtistAnimation(fig=fig, artists=artists, interval=60, blit=True)
        path = self.gen_path("turing", "vid", ".mp4")
        # path = self.gen_path("turing", "vid", ".gif")
        print(f"saving {len(artists)} frames")
        ani.save(path)
        self.video = path
        return super().__call__()


def example_video(
    run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
) -> bch.Bench:
    # run_cfg.auto_plot = False
    # run_cfg.use_sample_cache = True
    bench = bch.Bench("example_video", TuringPattern(), run_cfg=run_cfg, report=report)

    bench.plot_sweep(
        "Turing patterns with different parameters",
        # input_vars=[TuringPattern.param.alpha, TuringPattern.param.beta],
        input_vars=[TuringPattern.param.alpha],
        result_vars=[TuringPattern.param.video],
    )

    return bench


if __name__ == "__main__":
    run_cfg_ex = bch.BenchRunCfg()
    run_cfg_ex.level = 2
    run_cfg_ex.repeats = 2
    # run_cfg.only_hash_tag = True
    # run_cfg.use_sample_cache = True

    example_video(run_cfg_ex).report.show()
