import os
import pathlib

import pytest  # type: ignore

import gst


@pytest.mark.parametrize("attr", ["executable", "gisbase", "python_lib"])
def test_grass_has_attribute(grass, attr):
    assert hasattr(grass, attr)


@gst.require_grass
def assert_location_is_current(location: pathlib.Path) -> None:
    import grass.script as gscript

    gisenv = gscript.gisenv()
    current_location = os.path.join(gisenv["GISDBASE"], gisenv["LOCATION_NAME"])
    assert current_location == location.as_posix()


def test_grass_session_contextmanager(grass, tloc):
    with grass.session(tloc):
        assert_location_is_current(tloc)


def test_grass_session_decorator(grass, tloc):
    @grass.session(location=tloc)
    def inside_grass_session():
        assert_location_is_current(tloc)

    inside_grass_session()
