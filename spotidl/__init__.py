import tomli

from spotidl import spotidl_rs


with open("pyproject.toml", "rb") as toml_file:
    toml_data = tomli.load(toml_file)

project_data = toml_data.get("project", {})
__version__ = project_data.get("version")

del toml_data, project_data
