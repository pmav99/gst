import os
import pathlib
import sys

import pytest


if not os.environ.get("GST_GRASS_EXECUTABLE"):
    sys.exit(
        "You need to define $GST_GRASS_EXECUTABLE before running the tests. "
        "It's value must be the path to the GRASS GIS executable."
    )


TESTS_ROOT = pathlib.Path(__file__).parent
TESTS_GISDBASE = TESTS_ROOT / "gisdbase"
REPO_ROOT = TESTS_ROOT.parent

EPSG4326 = TESTS_GISDBASE / "epsg4326"

GRASS_ENV_VARIABLES = [
    # TODO uncomment GISBASE when #3772 gets resolved.
    # "GISBASE",
    "GISRC",
    "GIS_LOCK",
    "GRASS_PYTHON",
    "GRASS_ADDON_BASE",
]

# pytest parametrized
param_test_locations = pytest.mark.parametrize(
    "loc", [pytest.param(EPSG4326, id="epsg4326")]
)


def _normalize_mapsets(mapsets):
    """
    1. If `mapsets` is a string, convert it to a set containing the string
    2. We can't have a Location without the `PERMANENT` has not been specified, add it to the set.
    """
    if not mapsets:
        raise ValueError("You must specify a mapset!")
    if isinstance(mapsets, str):
        mapsets = set((mapsets,))
    else:
        mapsets = set(mapsets)
    if "PERMANENT" not in mapsets:
        mapsets.add("PERMANENT")
    return mapsets


def test_normalize_mapsets():
    assert _normalize_mapsets("asdf") == set(("asdf", "PERMANENT"))
    assert _normalize_mapsets(("asdf",)) == set(("asdf", "PERMANENT"))
    assert _normalize_mapsets("PERMANENT") == set(("PERMANENT",))
    assert _normalize_mapsets(("asdf", "PERMANENT")) == set(("asdf", "PERMANENT"))
    with pytest.raises(ValueError) as exc:
        _normalize_mapsets("")
    assert "you must specify a mapset" in str(exc).lower(), str(exc).lower()
