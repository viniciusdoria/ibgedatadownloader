import toml
from qgispluginci import changelog, utils

with open("pyproject.toml", encoding="utf8") as fd:
    config = toml.load(fd)

try:
    latest = changelog.ChangelogParser().latest_version()
except AttributeError as e:
    msg = "Nenhuma versão no formato major.minor.patch foi encontrada no changelog."
    raise Exception(msg) from e

utils.replace_in_file(
    f"{config['tool']['qgis-plugin-ci']['plugin_path']}/metadata.txt",
    r"^version=.*$",
    f"version={latest}",
)
