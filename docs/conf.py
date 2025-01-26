# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


from importlib import metadata
from nbsite.shared_conf import *  # noqa

copyright = "2025, Austin Gregg-Smith"  # pylint:disable=redefined-builtin
author = "Austin Gregg-Smith"
release = metadata.version("holobench")
project = f"bencher {release}"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions += [
    "sphinx.ext.napoleon",
    # "autoapi.extension",
    "nbsite.gallery",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = "pydata_sphinx_theme"
html_theme = "sphinx_rtd_theme"
# html_static_path = ["_static"]

autoapi_dirs = ["../bencher"]
autoapi_ignore = ["*example_*", "*example*", "*experimental*"]


numpydoc_show_class_members = False

autosummary_generate = True

nbsite_gallery_conf = {
    # "examples_dir": "examples",
    # "galleries": {},
    "default_extensions": ["*.ipynb", "*.py"],
    "examples_dir": ".",
    "galleries": {
        "reference": {
            "title": "Reference Gallery",
            "intro": (
                "Find the list of supported libraries on the `Integrations <../user_guide/Integrations.html>`_ page."
            ),
            "sections": [
                "ex1",
                "ex2",
            ],
            "skip_rst_notebook_directive": True,
        }
    },
}

nbsite_nbbuild_exclude_patterns = ["jupyter_execute/**"]
