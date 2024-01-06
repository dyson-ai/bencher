import numpy as np
import math
import taichi as ti
import taichi.math as tm
from video_writer import VideoWriter
import vedo
from vedo import Volume
from vedo.applications import Slicer3DPlotter, IsosurfaceBrowser
from copy import deepcopy
import bencher as bch
import panel as pn
import pyvista as pv

# https://www.degeneratestate.org/posts/2017/May/05/turing-patterns/

ti.init(arch=ti.vulkan)


W, H = 200, 200
pixels = ti.Vector.field(3, ti.f32, shape=(W, H))

# Du, Dv, feed, kill = 0.160, 0.080, 0.060, 0.062
# Du, Dv, feed, kill = 0.210, 0.105, 0.018, 0.051

# def setup_grid()
uv_grid = np.zeros((2, W, H, 2), dtype=np.float32)
uv_grid[0, :, :, 0] = 1.0
rand_rows = np.random.choice(range(W), 50)
rand_cols = np.random.choice(range(H), 50)
uv_grid[0, rand_rows, rand_cols, 1] = 1.0
uv = ti.Vector.field(2, ti.f32, shape=(2, W, H))
uv_deep = deepcopy(uv_grid)
uv.from_numpy(uv_grid)

values = ti.Vector.field(1, ti.f32, shape=(W, H))


palette = ti.Vector.field(4, ti.f32, shape=(5,))
# palette[0] = [0, 0, 0, 0]  # [0.0, 0.0, 0.0, 0.31372549]
# palette[1] = [0, 1, 0, 0.2]  # [1.0, 0.1843, 0.53333333, 0.376470588]
# palette[2] = [1.0, 1.0, 0.0, 0.2078431373]  # [0.854901961, 1.0, 0.5333333, 0.3882353]
# palette[3] = [1, 0, 0, 0.4]  # [0.376471, 1.0, 0.47843, 0.39215686]
# palette[4] = [1.0, 1.0, 1.0, 0.6]
palette[0] = [0.0, 0.0, 0.0, 0.3137]
palette[1] = [1.0, 0.1843, 0.53333, 0.37647]
palette[2] = [0.8549, 1.0, 0.53333, 0.388]
palette[3] = [0.376, 1.0, 0.478, 0.392]
palette[4] = [1.0, 1.0, 1.0, 1]


@ti.kernel
def compute(phase: int, Du: float, Dv: float, feed: float, kill: float):
    for i, j in ti.ndrange(W, H):
        cen = uv[phase, i, j]
        lapl = (
            uv[phase, i + 1, j]
            + uv[phase, i, j + 1]
            + uv[phase, i - 1, j]
            + uv[phase, i, j - 1]
            - 4.0 * cen
        )
        du = Du * lapl[0] - cen[0] * cen[1] * cen[1] + feed * (1 - cen[0])
        dv = Dv * lapl[1] + cen[0] * cen[1] * cen[1] - (feed + kill) * cen[1]
        val = cen + 0.5 * tm.vec2(du, dv)
        uv[1 - phase, i, j] = val


@ti.kernel
def render():
    for i, j in pixels:
        value = uv[0, i, j].y
        color = tm.vec3(0)
        if value <= palette[0].w:
            color = palette[0].xyz

        for k in range(4):
            c0 = palette[k]
            c1 = palette[k + 1]
            if c0.w < value < c1.w:
                a = (value - c0.w) / (c1.w - c0.w)
                color = tm.mix(c0.xyz, c1.xyz, a)

        pixels[i, j] = color


@ti.kernel
def get_val():
    for i, j in pixels:
        values[i, j] = uv[0, i, j].y


npgrip = []


from vedo import dataurl, Plotter, Mesh, Video

def wiggle_camera(self, scale=1, callback=None):
    import math

    dist = self.dist
    yaw = self.yaw
    pitch = self.pitch
    target = self.target

    for y in np.arange(0, 6.28, 0.1):
        self.set_camera(
            distance=dist,
            yaw=yaw + math.sin(y) * scale,
            pitch=pitch + math.cos(y) * scale,
            target=target,
        )






class SweepTuring(bch.ParametrizedSweep):
    # Du, Dv, feed, kill = 0.160, 0.080, 0.060, 0.062
    # Du, Dv, feed, kill = 0.210, 0.105, 0.018, 0.051

    # Du = bch.FloatSweep(default=0.160,bounds=(0.1,0.2))
    # Dv = bch.FloatSweep(default=0.080,bounds=(0.05,0.09))
    # feed = bch.FloatSweep(default=0.06,bounds=(0.06,0.18))
    # kill = bch.FloatSweep(default=0.062,bounds=(0.051,0.062))

    Du = bch.FloatSweep(default=0.160, bounds=(0.08, 0.40))
    Dv = bch.FloatSweep(default=0.08, bounds=(0.04, 0.10))
    feed = bch.FloatSweep(default=0.06, bounds=(0.03, 0.07))
    kill = bch.FloatSweep(default=0.062, bounds=(0.060, 0.064))

    rendermode = bch.IntSweep(default=0,bounds=(0,4))

    bitrate = bch.FloatSweep(default=1000, bounds=(100, 2000))

    duration = bch.FloatSweep(default=40)

    record_volume_vid = bch.BoolSweep(default=False)
    # resolution = bch.IntSweep(default=100)

    # Du = bch.FloatSweep(default=0.160,bounds=(0.08,0.40))
    # Dv = bch.FloatSweep(default=0.08,bounds=(0.04,0.10))
    # feed = bch.FloatSweep(default=0.06,bounds=(0.06,0.18))
    # kill = bch.FloatSweep(default=0.062,bounds=(0.051,0.062))

    vid = bch.ResultVideo()
    vol_vid = bch.ResultVideo()
    ref = bch.ResultReference()

    def __call__(self, **kwargs):
        global uv
        self.update_params_from_kwargs(**kwargs)
        uv.from_numpy(deepcopy(uv_grid))

        gui = ti.GUI("turing", res=W)
        vr = VideoWriter(gui)
        self.vid = bch.gen_video_path("turing")
        if self.record_volume_vid:
            self.vol_vid= bch.gen_video_path("turing_vol",".mp4")
            video = Video(self.vol_vid, fps=30, backend='ffmpeg') 
            plt = Plotter( axes=7,offscreen=False, interactive=0,size=(600,600))
            plt.azimuth(-45)
        stacked_volume = np.empty(shape=(W,H,self.duration))
        substeps = 60
        i=0
        for frame in range(self.duration):
            vr.update_gui(pixels)
            gui.set_image(pixels)
            get_val()
            stacked_volume[:,:,frame]= values.to_numpy().squeeze()
            if self.record_volume_vid:
                vol = Volume(stacked_volume)
                vol.mode(self.rendermode).cmap("jet")
                plt.add(vol)
                scale=0.25
                camera_lerp = bch.lerp(frame,0,self.duration,0,math.pi*2)
                plt.camera.Azimuth(math.sin(camera_lerp) * scale)
                plt.camera.Elevation(math.cos(camera_lerp) * scale)
                plt.show()
                video.add_frame()
            gui.show()
            for _ in range(substeps):
                compute(i % 2, self.Du, self.Dv, self.feed, self.kill)
                i += 1
            render()

        self.ref = bch.ResultReference(stacked_volume,container=pyvista_volume_container)
        vr.write(self.vid, self.bitrate)

        if self.record_volume_vid:
            plt.close()
            video.close()
        gui.close()
        return super().__call__()



def pyvista_volume_container(npdat,**kwargs):
    # vol = pv.wrap(npdat)
    # pn.extension('vtk')
    # return pn.pane.VTKVolume(npdat, display_slices=True)
    plotter = pv.Plotter()
    vol = pv.wrap(npdat)
    plotter.add_volume(vol)
    # plotter.add_volume_clip_plane(vol)

    return pn.panel(plotter.ren_win, orientation_widget=True, **kwargs)

if __name__ == "__main__":

    run_cfg = bch.BenchRunCfg()
    run_cfg.level = 4
    run_cfg.use_sample_cache = True
    run_cfg.run_tag = "13"
    bench = SweepTuring().to_bench(run_cfg)

    SweepTuring.param.Du.bounds = [0.13, 0.19]

    plot_kwargs = dict(width=600,height=600)
    # SweepTuring.param.Dv.bounds = [0.08, 0.09]

    row = pn.Row()
    bench.plot_sweep("turing", input_vars=[SweepTuring.param.Du],plot=False)
    # bench.report.append(bench.get_result().to_auto(**plot_kwargs))

    SweepTuring.param.Du.default = 0.145
    bench.plot_sweep("turing", input_vars=[SweepTuring.param.Dv], plot=False)
    # bench.report.append(bench.get_result().to_auto(**plot_kwargs))

    SweepTuring.param.Dv.default = 0.07
    bench.plot_sweep("turing", input_vars=[SweepTuring.param.feed], plot=False)
    bench.report.append(bench.get_result().to_auto(**plot_kwargs))

    # row.append(bench.get_result().to_auto(**plot_kwargs))

    SweepTuring.param.feed.default = 0.07
    bench.plot_sweep("turing", input_vars=[SweepTuring.param.kill], plot=False)
    # bench.report.append(bench.get_result().to_auto(**plot_kwargs))
    # row.append(bench.get_result().to_auto(**plot_kwargs))


    # bench.report.append(row)

    bench.report.show()

    exit()

    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.Du,SweepTuring.param.Dv])

    SweepTuring.param.Du.bounds = [0.13, 0.19]
    SweepTuring.param.Dv.bounds = [0.08, 0.09]
    run_cfg.level = 4
    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.Du,SweepTuring.param.Dv])

    run_cfg.level = 4

    SweepTuring.param.Du.default = 0.176
    SweepTuring.param.Dv.default = 0.0825
    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.feed,SweepTuring.param.kill])

    # SweepTuring.param.Du.default = 0.176
    # SweepTuring.param.Dv.default = 0.0825

    # bench.plot_sweep("turing",)

    SweepTuring.param.feed.default = 0.03
    SweepTuring.param.kill.default = 0.064

    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.Du,SweepTuring.param.Dv])
    SweepTuring.param.Du.bounds = None
    SweepTuring.param.Dv.bounds = None
    SweepTuring.param.feed.bounds = None
    SweepTuring.param.kill.bounds = None

    def box(name, center, width):
        var = bch.FloatSweep(default=center, bounds=(center - width, center + width))
        var.name = name
        return var

    wid = 0.001

    run_cfg.level = 2

    # bench.plot_sweep("turing",input_vars=[box("Du",0.176,wid),box("Dv",0.0825,wid),box("feed",0.03,wid),box("kill",0.064,wid)])

    # bench.plot_sweep("turing",input_vars=[box("Du",0.176,wid),box("Dv",0.0825,wid),box("feed",0.03,wid),box("kill",0.06,0.001)])

    # bench.plot_sweep("turing",input_vars=[box("Du",0.176,wid),box("Dv",0.00725,0.001),box("feed",0.03,wid),box("kill",0.06,0.001)])

    wid = 0.001
    run_cfg.level = 3

    bench.plot_sweep(
        "turing",
        input_vars=[box("Du", 0.176, wid), box("Dv", 0.00725, 0.001), box("feed", 0.03, wid)],
    )

    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.feed,SweepTuring.param.Dv])
    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.feed,SweepTuring.param.Dv])

    # SweepTuring.param.Dv.default = 0.0825

    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.feed,SweepTuring.param.kill])

    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.col])

    # bench.plot_sweep("turing",input_vars=[SweepTuring.param.bitrate])
    # bench.report.save_index()
    bench.report.show()
