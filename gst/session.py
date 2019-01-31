import logging
import os.path
import pathlib
import sys
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import delegator  # type: ignore

from .utils import resolve_grass_executable

logger = logging.getLogger(__name__)


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
        self.gisbase = self.get_gisbase()
        self.python_lib = self.gisbase / "etc/python"

    def get_gisbase(self) -> pathlib.Path:
        """ Return the path to the GRASS installation directory. """
        p = delegator.run(f"{self.executable} --config path")
        return pathlib.Path(p.out.strip()).resolve()


class Session(object):
    """
    A context manager that allows you to work with GRASS GIS without explicitly
    starting it.

    """

    grass: Grass
    gisdb: pathlib.Path
    location: pathlib.Path
    mapset: pathlib.Path

    _orig_env: Dict[str, str]
    _orig_path: str
    _orig_sys_path: List[str]
    _orig_python_path: str

    def __init__(
        self,
        location: Union[str, pathlib.Path],
        mapset: Union[str, pathlib.Path] = "PERMANENT",
        grass: Union[str, pathlib.Path, Grass] = None,
    ) -> None:
        self.location = pathlib.Path(location)
        self.mapset = self.location / mapset
        self.grass = grass if isinstance(grass, Grass) else Grass(grass)
        self.gisdbase = self.location.parent
        self._make_sanity_check()

    def _make_sanity_check(self) -> None:
        if not self.mapset.exists():
            msg = f"The mapset does not exist. Please create it first and try again: {self.mapset}"
            raise ValueError(msg)
        if not self.mapset.is_dir():
            msg = f"The Mapset exists, but is not a directory. Please check it out: {self.mapset}"
            raise ValueError(msg)

    def __enter__(self) -> None:
        logger.debug(f"Starting to setup GRASS context: {self.location}")
        # store original environment in order to restore them when we exit.
        self._orig_env = os.environ.copy()
        self._orig_sys_path = sys.path.copy()

        # Setup GRASS environment
        # The bulk of the work, will be done by `grass.script.setup.init()`
        # Although, at the moment, we can't import that function
        # unless we set GISBASE manually.
        # So, until that is resolved, let's set it
        os.environ["GISBASE"] = self.grass.gisbase.as_posix()

        # In order to import `grass.script.setup` though, we frst need
        # to add `python_lib` to `sys.path`.
        sys.path.append(self.grass.python_lib.as_posix())

        # OK the imports do work, so we are ready to initialize the GRASS session
        from grass.script.setup import init  # type: ignore

        init(
            gisbase=self.grass.gisbase.as_posix(),
            dbase=self.gisdbase.as_posix(),
            location=self.location.name,
            mapset=self.mapset.name,
        )

        # Not sure why, but the `bin` directory of the addons is not being added to
        # $PATH by `gsetup()`, so let's make sure it is there
        os.environ["PATH"] += os.pathsep + os.path.join(
            os.environ["GRASS_ADDON_BASE"], "bin"
        )
        logger.debug(f"Finished setting up GRASS context: {self.location}")
        logger.info(f"Entering GRASS session: {self.location}")

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        logger.debug(f"Starting to tear down GRASS context: {self.location}")
        from grass.script.setup import finish  # type: ignore

        finish()
        # Restore the original env
        os.environ.clear()
        os.environ.update(self._orig_env)
        sys.path = self._orig_sys_path
        logger.debug(f"Finished tearing down GRASS context: {self.location}")
        logger.info(f"Exiting GRASS session: {self.location}")
