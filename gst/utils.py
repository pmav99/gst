"""
Various utilities for the `gst` package.
"""
from __future__ import annotations

import logging
import os
import pathlib
import shutil
import typing
import uuid
from typing import Optional
from typing import Union

import decorator  # type: ignore

if typing.TYPE_CHECKING:
    import grass.pygrass.gis as ggis  # type: ignore


logger = logging.getLogger(__name__)


def _resolve_path(executable: Union[str, pathlib.Path]) -> pathlib.Path:
    resolved = shutil.which(executable)
    if resolved is None:
        raise ValueError(
            f"Please provide the path to the GRASS executable, not: {executable}"
        )
    path = pathlib.Path(resolved)
    return path


def _resolve_gst_grass_executable() -> pathlib.Path:
    resolved = os.environ.get("GST_GRASS_EXECUTABLE")
    if resolved is None:
        raise ValueError(
            f"Please set '$GST_GRASS_EXECUTABLE' to the path of the GRASS executable"
        )
    path = pathlib.Path(resolved)
    # shutil.which() ensures the path exists and it is an executable file.
    if not shutil.which(path):
        raise ValueError(
            f"Please set '$GST_GRASS_EXECUTABLE' to the path of the GRASS executable, "
            f"not: {path}"
        )
    return path


def resolve_grass_executable(
    executable: Optional[Union[str, pathlib.Path]] = None
) -> pathlib.Path:
    """
    Resolve the path to the GRASS `executable` and return it.

    If `executable` is specified, then the path will be resolved using `shutil.which`.
    If it is not specified, then the value of `$GST_GRASS_EXECUTABLE` will also be
    checked and resolved with `shutil.which`.

    The `$GST_GRASS_EXECUTABLE` has been introduced to make it easier to work with compiled
    from source GRASS versions, which often are not being added to `$PATH`

    If a path cannot be resolved, then a `ValueError` will be raised.

    Note: There is no check if the resolved executable is actually a grass one or not.

    Parameters
    ----------
    executable:
        The path to the GRASS executable.

    Raises
    ------
    ValueError:
        When neither `executable` nor `GST_GRASS_EXECUTABLE` has been set, or if they
        resolve to an non-existing path or to a non-executable file.

    """
    # If the user provides an explicit `executable` value, use it.
    # If not, try to use GST_GRASS_EXECUTABLE
    if executable:
        path = _resolve_path(executable)
    else:
        path = _resolve_gst_grass_executable()
    return path


@decorator.decorator
def require_grass(func, *args, **kwargs):
    """
    Functions decorated with this will raise `ValueError` if they are not called
    inside a GRASS session
    """
    if not os.environ.get("GIS_LOCK"):
        raise ValueError(
            f"function <{func.__name__}> needs to be called inside a GRASS session"
        )
    return func(*args, **kwargs)


__all__ = ["resolve_grass_executable", "require_grass"]


@require_grass
@decorator.contextmanager
def temp_region(*, raster: Optional[str] = None) -> "ggis.Region":
    """
    Context manager that restores current region on exit.

    Parameters
    ----------

    raster:
        If specified, then the region is set to match the provided map upon entering the
        context, while it will be restored to the original one on exit.  If `raster` is
        not specified, then the region will not be changed upon entering the context,
        nevertheless it will be restored on exit, so you can freely change it.

    """
    import grass.pygrass.gis as ggis

    original = ggis.Region()
    current = ggis.Region()
    if raster:
        current.from_rast(raster)
        current.write()
    try:
        yield current
    finally:
        original.write()


@require_grass
@decorator.contextmanager
def temp_mapset(
    *, mapset_name: Optional[str] = None, cleanup: bool = True
) -> "ggis.Mapset":
    """
    Context manager that creates a temporary mapset which gets removed on exit.

    Parameters
    ----------

    mapset_name:
        The name of the temporary mapset. If it is not provided, then a random hex
        will be used (via `uuid.uuid4().hex`).

    cleanup:
        If `cleanup` is `False` then the mapset will not be removed when the wrapped
        function returns (useful for e.g. tests).

    """
    import grass.pygrass.gis as ggis

    if mapset_name is None:
        mapset_name = uuid.uuid4().hex
    ggis.make_mapset(mapset_name)
    ggis.set_current_mapset(mapset_name)
    temp_mapset = ggis.Mapset(mapset_name)
    try:
        yield temp_mapset
    finally:
        ggis.set_current_mapset("PERMANENT")
        if cleanup:
            # remove the test mapset
            temp_mapset.delete()


@decorator.decorator
def with_temp_region(func, raster: Optional[str] = None, *args, **kwargs):
    """
    Decorator that creates a temporary Mapset before executing the wrapped function.

    Parameters
    ----------

    mapset_name:
        The name of the temporary mapset. If it is not provided, then the temporary
        mapset will use the `__qualname__` of the wrapped function.

    cleanup:
        If `cleanup` is `False` then the mapset will not be removed when the wrapped
        function returns (useful for e.g. tests).

    """
    with temp_region(raster=raster):
        return func(*args, **kwargs)


@decorator.decorator
def with_temp_mapset(
    func, mapset_name: Optional[str] = None, cleanup: bool = True, *args, **kwargs
):
    """
    Decorator that creates a temporary Mapset before executing the wrapped function.

    Parameters
    ----------

    mapset_name:
        The name of the temporary mapset. If it is not provided, then the temporary
        mapset will use the `__qualname__` of the wrapped function.

    cleanup:
        If `cleanup` is `False` then the mapset will not be removed when the wrapped
        function returns (useful for e.g. tests).

    """
    if not mapset_name:
        mapset_name = f"{func.__module__}_{func.__qualname__}"
        mapset_name = mapset_name.replace(".", "_")
    with temp_mapset(mapset_name=mapset_name, cleanup=cleanup):
        return func(*args, **kwargs)


__all__ = [
    "resolve_grass_executable",
    "require_grass",
    "temp_region",
    "temp_mapset",
    "with_temp_region",
    "with_temp_mapset",
]
