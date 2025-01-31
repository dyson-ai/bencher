import nbformat as nbf
from pathlib import Path


def convert_example_to_jupyter_notebook(filename: str):
    source_path = Path.home() / filename

    nb = nbf.v4.new_notebook()
    title = source_path.stem
    function_name = f"{source_path.stem}()"
    text = f"""# {title}"""

    code = "%%capture\n"

    example_code = source_path.read_text()
    split_code = example_code.split("""if __name__ == "__main__":""")
    code += split_code[0]

    code += f"""
bench={function_name}
"""

    code_results = """
from bokeh.io import output_notebook
output_notebook()
bench.get_result().to_auto_plots()
"""

    nb["cells"] = [
        nbf.v4.new_markdown_cell(text),
        nbf.v4.new_code_cell(code),
        nbf.v4.new_code_cell(code_results),
    ]
    output_path = Path(f"docs/reference/examples/ex_{title}.ipynb")
    # output_path.mkdir()
    output_path.write_text(nbf.writes(nb), encoding="utf-8")


if __name__ == "__main__":
    convert_example_to_jupyter_notebook(
        "/home/ags/projects/bencher/bencher/example/example_simple_float.py"
    )
