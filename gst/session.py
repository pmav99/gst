from __future__ import annotations

import logging
import os.path
import pathlib
import sys
from typing import Union

import decorator  # type: ignore

from .grass_bin import Grass
from .system_restore import restore_system_state
from .system_restore import save_system_state
from .system_restore import SystemState

logger = logging.getLogger(__name__)

__all__ = ["Session", "start_grass_session", "finish_grass_session"]


class Session(decorator.ContextManager):
    """
    A context manager that allows you to work with GRASS GIS without explicitly
    starting it.

    Attributes
    ----------
    location:
        The path to the GRASS Location
    mapset:
        The path to the GRASS Mapset
    grass:
        The path to the GRASS executable
    gisdbase:
    is_active:
        A boolean property indicating whether the session is active or not

    Parameters
    ----------

    location:
        The path to the GRASS Location
    mapset:
        The path to the GRASS Mapset
    grass:
        The GRASS executable.

    Raises
    ------
    ValueError:
        If the GRASS executable cannot be found.

    """

    location: pathlib.Path
    mapset: pathlib.Path
    grass: Grass
    gisdbase: pathlib.Path
    _is_active: bool

    def __init__(
        self,
        location: Union[str, pathlib.Path],
        mapset: Union[str, pathlib.Path] = "PERMANENT",
        grass: Union[str, pathlib.Path, Grass] = None,
    ) -> None:
        self.location = pathlib.Path(location).resolve()
        self.mapset = self.location / mapset
        self.grass = grass if isinstance(grass, Grass) else Grass(grass)
        self.gisdbase = self.location.parent
        self._is_active = False
        # We run the sanity check at the end of __init__ because we need to first
        # convert mapset to a pathlib.Path instance.
        _mapset_sanity_check(self.mapset)

    @property
    def is_active(self):
        return self._is_active

    def __repr__(self):
        return f"<GRASS Session: {self.mapset.as_posix()}>"

    def __enter__(self) -> Session:
        logger.debug("Starting to setup GRASS context: {self.location}")
        # store original environment in order to restore them when we exit.
        self._original_state = start_grass_session(
            self.grass, self.location, self.mapset
        )

        # mark the session as active
        self._is_active = True

        logger.debug(f"Finished setting up GRASS context: {self.location}")
        logger.info(f"Entering GRASS session: {self.location}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        logger.debug(f"Starting to tear down GRASS context: {self.location}")
        finish_grass_session(self._original_state)
        self._is_active = False
        logger.debug(f"Finished tearing down GRASS context: {self.location}")
        logger.info(f"Exiting GRASS session: {self.location}")


def _mapset_sanity_check(mapset: pathlib.Path) -> None:
    if not mapset.exists():
        msg = (
            f"The mapset does not exist. Please create it first and try again: {mapset}"
        )
        raise ValueError(msg)
    if not mapset.is_dir():
        msg = (
            f"The Mapset exists, but is not a directory. Please check it out: {mapset}"
        )
        raise ValueError(msg)


def start_grass_session(
    grass_bin: Grass,
    location: pathlib.Path,
    mapset: pathlib.Path = pathlib.Path("PERMANENT"),
) -> SystemState:
    """ Start a grass session """

    _mapset_sanity_check(location / mapset)
    # store original environment in order to restore it when we finish the session
    original_state: SystemState = save_system_state()

    # Setup GRASS environment
    # The bulk of the work, will be done by `grass.script.setup.init()`
    # Although, at the moment, we can't import that function
    # unless we set GISBASE manually.
    # So, until that is resolved, let's set it
    os.environ["GISBASE"] = grass_bin.gisbase.as_posix()

    # In order to import `grass.script.setup` though, we first need
    # to add `python_lib` to `sys.path`.
    sys.path.append(grass_bin.python_lib.as_posix())

    # OK the imports do work, so we are ready to initialize the GRASS session
    from grass.script.setup import init  # type: ignore

    init(
        gisbase=grass_bin.gisbase.as_posix(),
        dbase=location.parent.as_posix(),
        location=location.name,
        mapset=mapset.name,
    )

    # Not sure why, but the directories of the GRASS addons are not being added to
    # $PATH by `gsetup()`, so let's make sure they are added.
    addon_paths = [
        # os.path.join(os.environ["GRASS_ADDON_BASE"], "bin"),
        os.path.join(os.environ["GRASS_ADDON_BASE"], "etc"),
        os.path.join(os.environ["GRASS_ADDON_BASE"], "scripts"),
    ]
    os.environ["PATH"] += os.pathsep.join(addon_paths)
    return original_state


def finish_grass_session(original_state: SystemState) -> None:
    """ Finish a GRASS session """
    from grass.script.setup import finish  # type: ignore

    finish()
    restore_system_state(original_state)
