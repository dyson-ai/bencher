import rerun as rr
import bencher as bch
import panel as pn


rr.init("rerun_example_local", spawn=True)
file_path = "dat1.rrd"
rr.save(file_path)

rr.log("s1", rr.Scalar(1))
rr.log("s1", rr.Scalar(4))
rr.log("s1", rr.Scalar(2))

local = True

if local:
    row = pn.Row()
    # row.append(rrd_to_pane("http://localhost:8001/dat2.rrd"))

    row.append(bch.rrd_to_pane("http://127.0.0.1:8001/dat2.rrd"))
    # row.append(to_pane("home/ags/projects/bencher/dat1.rrd"))
    row.show()
else:
    # publish data to a github branch
    bch.publish_and_view_rrd(
        file_path,
        remote="https://github.com/dyson-ai/bencher.git",
        branch_name="test_rrd",
        content_callback=bch.github_content,
    ).show()
