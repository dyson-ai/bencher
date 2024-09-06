from .utils import publish_file
import logging
import panel as pn
from rerun.legacy_notebook import as_html


def rrd_to_pane(url: str, version: str = None):  # pragma: no cover
    if version is None:
        version = "0.18.2"  # TODO find a better way of doing this
    return pn.pane.HTML(
        f'<iframe src="https://app.rerun.io/version/{version}/?url={url}" width=1800 height=1000></iframe>'
    )


def publish_and_view_rrd(
    file_path: str, remote: str, branch_name, content_callback: callable, version: str = None
):  # pragma: no cover
    as_html()
    publish_file(file_path, remote=remote, branch_name="test_rrd")
    publish_path = content_callback(remote, branch_name, file_path)
    logging.info(publish_path)
    return rrd_to_pane(publish_path, version=version)
