import bencher as bch
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import ArtistAnimation


def random_initialiser(shape):
    return (
        np.random.normal(loc=0, scale=0.05, size=shape),
        np.random.normal(loc=0, scale=0.05, size=shape),
    )


def laplacian1D(a, dx):
    return (-2 * a + np.roll(a, 1, axis=0) + np.roll(a, -1, axis=0)) / (dx**2)


def laplacian2D(a, dx):
    return (
        -4 * a
        + np.roll(a, 1, axis=0)
        + np.roll(a, -1, axis=0)
        + np.roll(a, +1, axis=1)
        + np.roll(a, -1, axis=1)
    ) / (dx**2)


"""
Some utility functions for blog post on Turing Patterns.
"""

import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np


class BaseStateSystem:
    """
    Base object for "State System".

    We are going to repeatedly visualise systems which are Markovian:
    the have a "state", the state evolves in discrete steps, and the next
    state only depends on the previous state.

    To make things simple, I'm going to use this class as an interface.
    """

    def __init__(self):
        raise NotImplementedError()

    def initialise(self):
        raise NotImplementedError()

    def initialise_figure(self):
        fig, ax = plt.subplots()
        return fig, ax

    def update(self):
        raise NotImplementedError()

    def draw(self, ax):
        raise NotImplementedError()

    def plot_time_evolution(self, filename, n_steps=30):
        """
        Creates a gif from the time evolution of a basic state syste.
        """
        self.initialise()
        fig, ax = self.initialise_figure()

        def step(t):
            self.update()
            self.draw(ax)

        anim = animation.FuncAnimation(fig, step, frames=np.arange(n_steps), interval=20)
        anim.save(filename=filename, dpi=60, fps=10, writer="ffmpeg")
        plt.close()

    def plot_evolution_outcome(self, filename, n_steps):
        """
        Evolves and save the outcome of evolving the system for n_steps
        """
        self.initialise()
        fig, ax = self.initialise_figure()

        for _ in range(n_steps):
            self.update()

        self.draw(ax)
        fig.savefig(filename)
        plt.close()


class TwoDimensionalRDEquations(BaseStateSystem):
    def __init__(
        self,
        Da,
        Db,
        Ra,
        Rb,
        initialiser=random_initialiser,
        width=1000,
        height=1000,
        dx=1,
        dt=0.1,
        steps=1,
    ):
        self.Da = Da
        self.Db = Db
        self.Ra = Ra
        self.Rb = Rb

        self.initialiser = initialiser
        self.width = width
        self.height = height
        self.shape = (width, height)
        self.dx = dx
        self.dt = dt
        self.steps = steps

    def initialise(self):
        self.t = 0
        self.a, self.b = self.initialiser(self.shape)

    def update(self):
        for _ in range(self.steps):
            self.t += self.dt
            self._update()

    def _update(self):
        # unpack so we don't have to keep writing "self"
        a, b, Da, Db, Ra, Rb, dt, dx = (
            self.a,
            self.b,
            self.Da,
            self.Db,
            self.Ra,
            self.Rb,
            self.dt,
            self.dx,
        )

        La = laplacian2D(a, dx)
        Lb = laplacian2D(b, dx)

        delta_a = dt * (Da * La + Ra(a, b))
        delta_b = dt * (Db * Lb + Rb(a, b))

        self.a += delta_a
        self.b += delta_b

    def draw(self, ax):
        ax[0].clear()
        ax[1].clear()

        ax[0].imshow(self.a, cmap="jet")
        ax[1].imshow(self.b, cmap="brg")

        # ax[0].grid(b=False)
        # ax[1].grid(b=False)

        ax[0].set_title("A, t = {:.2f}".format(self.t))
        ax[1].set_title("B, t = {:.2f}".format(self.t))

    def initialise_figure(self):
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
        return fig, ax


Da, Db, alpha, beta = 1, 100, -0.005, 10


def Ra(a, b):
    return a - a**3 - b + alpha


def Rb(a, b):
    return (a - b) * beta


width = 100
dx = 1
dt = 0.001

TwoDimensionalRDEquations(
    Da, Db, Ra, Rb, width=width, height=width, dx=dx, dt=dt, steps=100
).plot_evolution_outcome("2dRD.png", n_steps=150)

plt.show()

# https://www.degeneratestate.org/posts/2017/May/05/turing-patterns/


# # code from https://ipython-books.github.io/124-simulating-a-partial-differential-equation-reaction-diffusion-systems-and-turing-patterns/
# class TuringPattern(bch.ParametrizedSweep):
#     alpha = bch.FloatSweep(default=2.8e-4, bounds=(2e-4, 5e-3))
#     beta = bch.FloatSweep(default=5e-3, bounds=(1e-3, 9e-3))
#     tau = bch.FloatSweep(default=0.1, bounds=(0.01, 0.5))
#     k = bch.FloatSweep(default=-0.005, bounds=(-0.01, 0.01))

#     size = bch.IntSweep(default=50, bounds=(30, 200), doc="size of the 2D grid")
#     time = bch.FloatSweep(default=20.0, bounds=(1, 100), doc="total time of simulation")
#     dt = bch.FloatSweep(default=0.001, doc="simulation time step")

#     video = bch.ResultVideo()

#     def laplacian(self, Z, dx):
#         Ztop = Z[0:-2, 1:-1]
#         Zleft = Z[1:-1, 0:-2]
#         Zbottom = Z[2:, 1:-1]
#         Zright = Z[1:-1, 2:]
#         Zcenter = Z[1:-1, 1:-1]
#         return (Ztop + Zleft + Zbottom + Zright - 4 * Zcenter) / dx**2

#     def update(self, U, V, dx):
#         # We compute the Laplacian of u and v.
#         deltaU = self.laplacian(U, dx)
#         deltaV = self.laplacian(V, dx)
#         # We take the values of u and v inside the grid.
#         Uc = U[1:-1, 1:-1]
#         Vc = V[1:-1, 1:-1]
#         # We update the variables.
#         U[1:-1, 1:-1], V[1:-1, 1:-1] = (
#             Uc + self.dt * (self.alpha * deltaU + Uc - Uc**3 - Vc + self.k),
#             Vc + self.dt * (self.beta * deltaV + Uc - Vc) / self.tau,
#         )
#         # Neumann conditions: derivatives at the edges
#         # are null.
#         for Z in (U, V):
#             Z[0, :] = Z[1, :]
#             Z[-1, :] = Z[-2, :]
#             Z[:, 0] = Z[:, 1]
#             Z[:, -1] = Z[:, -2]

#     def __call__(self, **kwargs):
#         self.update_params_from_kwargs(**kwargs)

#         n = int(self.time / self.dt)  # number of iterations
#         dx = 2.0 / self.size  # space step

#         U = np.random.rand(self.size, self.size)
#         V = np.random.rand(self.size, self.size)

#         fig, ax = plt.subplots(frameon=False, figsize=(2, 2))
#         fig.set_tight_layout(True)
#         ax.set_axis_off()

#         artists = []

#         for i in range(n):
#             self.update(U, V, dx)
#             if i % 500 == 0:
#                 artists.append([ax.imshow(U)])

#         ani = ArtistAnimation(fig=fig, artists=artists, interval=60, blit=True)
#         path = self.gen_path("turing", "vid", ".mp4")
#         # path = self.gen_path("turing", "vid", ".gif")
#         print(f"saving {len(artists)} frames")
#         ani.save(path)
#         self.video = path
#         return super().__call__()


# def example_video(
#     run_cfg: bch.BenchRunCfg = bch.BenchRunCfg(), report: bch.BenchReport = bch.BenchReport()
# ) -> bch.Bench:
#     # run_cfg.auto_plot = False
#     # run_cfg.use_sample_cache = True
#     bench = bch.Bench("example_video", TuringPattern(), run_cfg=run_cfg, report=report)

#     bench.plot_sweep(
#         "Turing patterns with different parameters",
#         input_vars=[TuringPattern.param.alpha, TuringPattern.param.beta],
#         # input_vars=[TuringPattern.param.alpha],
#         result_vars=[TuringPattern.param.video],
#     )

#     return bench


# if __name__ == "__main__":
#     run_cfg_ex = bch.BenchRunCfg()
#     run_cfg_ex.level = 2

#     example_video(run_cfg_ex).report.show()
