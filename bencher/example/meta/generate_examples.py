import nbformat as nbf
from pathlib import Path


def convert_example_to_jupyter_notebook(filename: str, output_path: str):
    # print
    source_path = Path(filename)

    nb = nbf.v4.new_notebook()
    title = source_path.stem
    function_name = f"{source_path.stem}()"
    text = f"""# {title}"""

    code = "%%capture\n"

    example_code = source_path.read_text(encoding="utf-8")
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
    output_path = Path(f"docs/reference/{output_path}/ex_{title}.ipynb")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(nbf.writes(nb), encoding="utf-8")


if __name__ == "__main__":
    convert_example_to_jupyter_notebook(
        "/workspaces/bencher/bencher/example/inputs_1D/example_1_in_1_out.py", "1D"
    )
    convert_example_to_jupyter_notebook(
        "/workspaces/bencher/bencher/example/inputs_1D/example_1_in_2_out.py", "1D"
    )

    convert_example_to_jupyter_notebook(
        "/workspaces/bencher/bencher/example/inputs_1D/example_1_in_2_out_repeats.py", "1D"
    )

    convert_example_to_jupyter_notebook(
        "/workspaces/bencher/bencher/example/example_simple_float.py", "1D"
    )
