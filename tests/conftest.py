import pathlib
import shutil

import pytest  # type: ignore

import gst.session
from . import _normalize_mapsets
from . import TESTS_GISDBASE


@pytest.fixture
def grass_bin():
    return gst.Grass()


@pytest.fixture
def gsession(tmpdir, grass_bin):
    """
    A pytest fixture that creates a `gst.Session` object.

    The location and the mapset must exist.
    """

    def inner(location, mapsets="PERMANENT"):
        test_location = tmpdir / "gisdbase" / location
        for mapset in _normalize_mapsets(mapsets):
            test_mapset = test_location / mapset
            shutil.copytree(TESTS_GISDBASE / location / mapset, test_mapset)
        session = grass_bin.session(test_location)
        return session

    return inner


@pytest.fixture
def epsg4326(gsession):
    """ Return a GRASS session using EPSG4326 Location """
    session = gsession("epsg4326", "PERMANENT")
    return session
