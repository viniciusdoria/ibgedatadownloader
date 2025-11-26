"""
Concentra os metadados sobre o plugin para fácil acesso.

`Saiba mais. <https://packaging.python.org/pt-br/latest/guides/single-sourcing-package-version/>`_
"""

from __future__ import annotations

import unicodedata
from configparser import ConfigParser
from datetime import date
from pathlib import Path
from typing import Final

__all__ = [
    "__author__",
    "__copyright__",
    "__email__",
    "__license__",
    "__summary__",
    "__title__",
    "__uri__",
    "__version__",
]


DIR_PLUGIN_ROOT: Final[Path] = Path(__file__).parent
PLG_METADATA_FILE: Final[Path] = DIR_PLUGIN_ROOT.resolve() / "metadata.txt"


def plugin_metadata_as_dict() -> dict[str, dict[str, str]]:
    """
    Reads metadata.txt and returns it as a dictionary of dictionaries.

    :raises FileNotFoundError: if metadata.txt not found
    :raises Exception: if metadata.txt does not contain a [general] section or some required field
    :return: Dictionary of dictionaries, where each key represents a section of metadata.txt
    """
    if not PLG_METADATA_FILE.is_file():
        msg = f"Plugin metadata.txt not found at {PLG_METADATA_FILE.parent}"
        raise FileNotFoundError(msg)

    config = ConfigParser()
    config.read(PLG_METADATA_FILE.resolve(), encoding="UTF-8")
    metadata = {s: dict(config.items(s)) for s in config.sections()}

    if metadata.get("general") is None:
        msg = f"No [general] section in {PLG_METADATA_FILE}"
        raise Exception(msg)

    required = ("name", "qgisminimumversion", "description", "about", "version", "author", "repository")
    missing = [field for field in required if not metadata["general"].get(field)]
    if missing:
        msg = f"Required fields missing from [general] section in metadata.txt: {', '.join(missing)}"
        raise Exception(msg)

    return metadata


# store full metadata.txt as dict into a var
__plugin_md__ = plugin_metadata_as_dict()

__author__: str = __plugin_md__["general"]["author"]
__copyright__: str = f"2022 - {date.today().year}, {__author__}"
__email__: str | None = __plugin_md__["general"].get("email") or None
__icon_path__: Path | None = (
    DIR_PLUGIN_ROOT.resolve() / __plugin_md__["general"]["icon"] if __plugin_md__["general"].get("icon") else None
)
__keywords__: list[str] = [t.strip() for t in __plugin_md__["general"].get("tags", "").split(",")]
__license__: str = "GPLv2+"
__summary__: str = f"{__plugin_md__['general'].get('description', '')}\n{__plugin_md__['general'].get('about', '')}"

__title__: str = __plugin_md__["general"]["name"]
__title_clean__: str = "".join(char for char in unicodedata.normalize("NFD", __title__) if char.isalnum())

__uri_homepage__: str | None = __plugin_md__["general"].get("homepage") or None
__uri_repository__: str = __plugin_md__["general"]["repository"]
__uri_tracker__: str | None = __plugin_md__["general"].get("tracker") or None
__uri__: str = __uri_repository__

__version__: str = __plugin_md__["general"]["version"]
__version_info__: tuple[int | str, ...] = tuple(
    int(num) if num.isdigit() else num for num in (__version__).replace("-", ".", 1).split(".")
)


if __name__ == "__main__":
    print(f"Plugin: {__title__}")
    print(f"By: {__author__}")
    print(f"Version: {__version__}")
    print(f"Description: {__summary__}")
    print(f"Repository: {__uri_repository__}")
    print(f"Icon: {__icon_path__}")
    general_md = __plugin_md__["general"]
    qgis_max_ver = general_md.get("qgismaximumversion") or general_md["qgisminimumversion"].split(".", 1)[0] + ".99"
    print(f"For: {general_md['qgisminimumversion']} > QGIS > {qgis_max_ver}")

    print(__title_clean__)
