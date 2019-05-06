import os
import pathlib

import pytest  # type: ignore

import gst
from . import param_test_locations
from . import TESTS_GISDBASE


@pytest.mark.parametrize("attr", ["executable", "gisbase", "python_lib"])
def test_grass_has_attribute(grass_bin, attr):
    assert hasattr(grass_bin, attr)


@gst.require_grass
def assert_location_is_current(location: pathlib.Path) -> None:
    import grass.script as gscript

    gisenv = gscript.gisenv()
    current_location = os.path.join(gisenv["GISDBASE"], gisenv["LOCATION_NAME"])
    assert current_location == location.as_posix()


@param_test_locations
def test_grass_session_contextmanager(grass_bin, loc):
    with grass_bin.session(loc):
        assert_location_is_current(loc)


@param_test_locations
def test_grass_session_decorator(grass_bin, loc):
    @grass_bin.session(location=loc)
    def inside_grass_session():
        assert_location_is_current(loc)

    inside_grass_session()
