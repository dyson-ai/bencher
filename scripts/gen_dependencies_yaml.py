# takes a pyproject.toml files and generates a dependencies.yaml file.
import tomli

with open("pyproject.toml", encoding="utf-8") as f:
    pyproject_dict = tomli.loads(f.read())

deps_yaml = ["pip:"]

for dep in pyproject_dict["project"]["optional-dependencies"]["test"]:
    deps_yaml.append(f"    test: {dep}")

deps_yaml.append("")
for dep in pyproject_dict["project"]["dependencies"]:
    deps_yaml.append(f"    buildrun: {dep}")

with open("dependencies.yaml", "w", encoding="utf-8") as f:
    for dep in deps_yaml:
        f.write(f"{dep}\n")
