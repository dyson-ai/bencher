import bencher as bch
import numpy as np
import rerun as rr
import rerun.blueprint as rrb
import panel as pn


my_blueprint = rrb.Blueprint(
    rrb.Horizontal(
        rrb.BarChartView(),
        rrb.Vertical(
            rrb.Spatial2DView(),
            rrb.Spatial3DView(),
        ),
    ),
)


# rr.init("rerun_example_my_blueprint", spawn=True, default_blueprint=my_blueprint)


rr.init(
    "rerun_example_my_blueprint",
    # spawn=True,
)


savepath = "dat.rrd"
rr.save(savepath)

# rr.send_blueprint(my_blueprint, make_active=True)
# rr.log("lol1", rr.Points2D([0, 1]))
# rr.log("lol2", rr.Points2D([1, 1]))
rr.log("s1", rr.Scalar(1))
rr.log("s1", rr.Scalar(2))
rr.log("s1", rr.Scalar(1))
rr.log("s1", rr.Scalar(2))

# exit()
if True:
    br = bch.BenchReport("test_rrd11")

    def publish_args(branch_name):
        return (
            "https://github.com/dyson-ai/bencher.git",
            f"https://github.com/dyson-ai/bencher/blob/{branch_name}",
        )

    def github_content(branch_name, filename):
        return f"https://raw.githubusercontent.com/dyson-ai/bencher/{branch_name}/{filename}"

    br.publish_rrd(savepath, remote_callback=publish_args)
    # bch.bench_report.BenchPlotServer.
    # rr.memory.memory_recording.
    # rr.recording_stream.get_data_recording.
    # pn.pane.HTML(rr.as_html).show)_
    # rr.start_web_viewer_server()
    # from rerun.notebook import as_html
    # print(as_html())
    # pn.pane.HTML(as_html()).show()

    # https://raw.githubusercontent.com/dyson-ai/bencher/test_rrd/dat.rrd

    def rrd_to_pane(url: str, version: str = "0.16.1"):
        return pn.pane.HTML(
            f'<iframe src="https://app.rerun.io/version/{version}/?url={url}" width=1800 height=1000></iframe>'
        )

    def rdd_to_pane2(branch_name, filename):
        print(github_content(branch_name, filename))
        return rrd_to_pane(github_content(branch_name, filename))

    # print(github_content(branch_name, savepath))

    rdd_to_pane2(br.bench_name, savepath).show()

    # rrd_to_pane("https://app.rerun.io/version/0.14.1/examples/arkit_scenes.rrd", "0.14.1").show()

    # rrd_to_pane("https://github.com/dyson-ai/bencher/test_rrd/dat.rrd?raw=true").show()

    # pn.pane.HTML(
    #     """<iframe src="https://app.rerun.io/version/0.16.1/?url=https://raw.githubusercontent.com/dyson-ai/bencher/test_rrd/dat.rrb" width=1000 height=1000></iframe>
    # """,
    # ).show()

    # pn.pane.HTML(
    #     """<iframe src="https://app.rerun.io/version/0.14.1/?url=https://app.rerun.io/version/0.14.1/examples/arkit_scenes.rrd" width=1000 height=1000></iframe>
    # """,
    # ).show()
