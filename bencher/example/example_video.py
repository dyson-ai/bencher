import bencher as bch
import numpy as np
from PIL import Image

def apply_colormap(data):
    """Apply a viridis-like colormap to the data"""
    # Create a simple blue-green-red colormap
    colors = np.array([
        [0, 0, 143],      # dark blue
        [0, 255, 255],    # cyan
        [0, 255, 0],      # green
        [255, 255, 0],    # yellow
        [255, 0, 0]       # red
    ])
    
    # Normalize data to [0, 1]
    normalized = (data - data.min()) / (data.max() - data.min())
    
    # Map normalized values to color indices
    indices = (normalized * (len(colors) - 1)).astype(int)
    
    # Create RGB array
    rgb = np.zeros((*data.shape, 3), dtype=np.uint8)
    
    # Interpolate between colors
    for i in range(len(colors) - 1):
        mask = (indices == i)
        if i < len(colors) - 1:
            # Calculate interpolation factor
            factor = (normalized - i/(len(colors)-1)) * (len(colors)-1)
            factor = factor[mask]
            # Interpolate between current and next color
            rgb[mask] = (colors[i] * (1-factor[:, np.newaxis]) + 
                        colors[i+1] * factor[:, np.newaxis]).astype(np.uint8)
    
    # Handle the last color
    rgb[indices == len(colors)-1] = colors[-1]
    
    return rgb

# code from https://ipython-books.github.io/124-simulating-a-partial-differential-equation-reaction-diffusion-systems-and-turing-patterns/
class TuringPattern(bch.ParametrizedSweep):
    alpha = bch.FloatSweep(default=2.8e-4, bounds=(2e-4, 5e-3))
    beta = bch.FloatSweep(default=5e-3, bounds=(1e-3, 9e-3))
    tau = bch.FloatSweep(default=0.1, bounds=(0.01, 0.5))
    k = bch.FloatSweep(default=-0.005, bounds=(-0.01, 0.01))

    size = bch.IntSweep(default=30, bounds=(30, 200), doc="size of the 2D grid")
    time = bch.FloatSweep(default=20.0, bounds=(1, 100), doc="total time of simulation")
    dt = bch.FloatSweep(default=0.001, doc="simulation time step")

    video = bch.ResultVideo()
    score = bch.ResultVar()
    img = bch.ResultImage()

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

        vid_writer = bch.VideoWriter()
        for i in range(n):
            self.update(U, V, dx)
            if i % 500 == 0:
                # Apply colormap to create RGB image
                rgb = apply_colormap(U)
                # Create PIL image with alpha channel
                img = Image.fromarray(rgb, 'RGB').convert('RGBA')
                # Resize image
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                # Convert back to numpy array
                rgb_alpha = np.array(img)
                vid_writer.append(rgb_alpha)

        self.img = bch.add_image(rgb_alpha)
        self.video = vid_writer.write()
        self.score = self.alpha + self.beta
        return super().__call__()


def example_video(run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None) -> bch.Bench:
    bench = TuringPattern().to_bench(run_cfg, report)

    bench.plot_sweep(
        "Turing patterns with different parameters",
        input_vars=["alpha", "beta"],
        result_vars=[TuringPattern.param.video],
    )

    return bench


def example_video_tap(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:  # pragma: no cover
    bench = TuringPattern().to_bench(run_cfg=run_cfg, report=report)
    res = bench.plot_sweep(input_vars=["alpha", "beta"])

    bench.report.append(res.to_video_grid(result_types=(bch.ResultVideo)))

    res = bench.plot_sweep(input_vars=["alpha"])
    bench.report.append(
        res.to_video_grid(
            result_types=(bch.ResultVideo),
            compose_method_list=[bch.ComposeType.right],
        )
    )

    return bench


if __name__ == "__main__":
    run_cfg_ex = bch.BenchRunCfg()
    run_cfg_ex.level = 2
    run_cfg_ex.cache_samples = True
    run_cfg_ex.only_hash_tag = True

    # example_video(run_cfg_ex).report.show()
    example_video_tap(run_cfg_ex).report.show()
