import logging
import os.path
import pathlib
import sys
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import decorator  # type: ignore
import delegator  # type: ignore

from .system_restore import restore_system_state
from .system_restore import save_system_state
from .utils import resolve_grass_executable

logger = logging.getLogger(__name__)

__all__ = ["Grass"]


class Grass(object):
    """
    A wrapper around a GRASS GIS installation.

    Attributes
    ----------
    executable:
        The path to the grass executable
    gisbase:
        The path to the grass installation directory
    python_lib:
        The path to the GRASS python library

    Parameters
    ----------

    executable:
        The absolute path to the grass executable. To make it easier to work with
        development versions of GRASS, specifying the full path If it is not specified,
        then we check if the variable

    Raises
    ------
    ValueError:
        If the GRASS executable cannot be found.
    """

    # Instance attributes type declarations
    executable: pathlib.Path
    gisbase: pathlib.Path
    python_lib: pathlib.Path

    def __init__(self, executable: Optional[Union[str, pathlib.Path]] = None) -> None:
        self.executable = resolve_grass_executable(executable)
        self.gisbase = self._get_gisbase()
        self.python_lib = self.gisbase / "etc/python"
        logger.debug(f"GRASS: {self.executable}")

    def _get_gisbase(self) -> pathlib.Path:
        """ Return the path to the GRASS installation directory. """
        p = delegator.run(f"{self.executable} --config path")
        return pathlib.Path(p.out.strip()).resolve()
