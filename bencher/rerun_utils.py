from .utils import publish_file
import logging
import panel as pn


def rrd_to_pane(url: str, version: str = "0.16.1"):
    return pn.pane.HTML(
        f'<iframe src="https://app.rerun.io/version/{version}/?url={url}" width=1800 height=1000></iframe>'
    )


def publish_and_view_rrd(file_path: str, remote: str, branch_name, content_callback: callable):
    publish_file(
        file_path, remote="https://github.com/dyson-ai/bencher.git", branch_name="test_rrd"
    )

    publish_path = content_callback(remote, branch_name, file_path)
    logging.info(publish_path)
    return rrd_to_pane(publish_path)
