import os
import shutil
import sys

import pytest  # type: ignore

import gst.session
from . import GRASS_ENV_VARIABLES
from . import param_test_locations


@param_test_locations
def test_repr(grass_bin, loc):
    grass_session = gst.session.Session(grass=grass_bin, location=loc)
    assert loc.as_posix() in str(grass_session)


@param_test_locations
def test_session_is_active(grass_bin, loc):
    session = gst.session.Session(grass=grass_bin, location=loc)
    assert session.is_active is False
    with session:
        assert session.is_active is True
    assert session.is_active is False


@param_test_locations
def test_we_can_import_grass(grass_bin, loc):
    with gst.session.Session(grass=grass_bin, location=loc):
        import grass  # type: ignore
        import grass.script  # type: ignore


@param_test_locations
def test_environment_is_teared_down_cleanly(grass_bin, loc):
    orig_env = os.environ.copy()
    orig_sys_path = sys.path.copy()
    with gst.session.Session(grass=grass_bin, location=loc):
        session_env = os.environ.copy()
        session_sys_path = sys.path.copy()
        assert orig_env != session_env
        assert orig_sys_path != session_sys_path
    assert orig_sys_path == sys.path.copy()
    assert orig_env == os.environ.copy()


@pytest.mark.parametrize("env", GRASS_ENV_VARIABLES)
def test_grass_env_variables_are_being_setup_and_teared_down(epsg4326, env):
    assert os.environ.get(env) is None
    with epsg4326:
        assert os.environ.get(env) is not None
    assert os.environ.get(env) is None


@pytest.mark.parametrize("env", GRASS_ENV_VARIABLES)
def test_decorator(epsg4326, env):

    # Define the function that will run inside the GRASS session
    @epsg4326
    def inside_grass_session():
        assert env in os.environ
        assert shutil.which("r.report")

    # run the tests
    assert env not in os.environ
    assert not shutil.which("r.report")
    inside_grass_session()
    assert env not in os.environ
    assert not shutil.which("r.report")
