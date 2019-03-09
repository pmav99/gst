"""
Various utilities for the `gst` package.
"""
import logging
import os
import pathlib
import shutil
from typing import Optional
from typing import Union


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

    Note: There is no check if the resoved executable is actually a grass one or not.

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


__all__ = ["resolve_grass_executable"]
