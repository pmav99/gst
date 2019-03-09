import os
import pathlib
import shutil
import sys

import pytest  # type: ignore

import gst.session


@pytest.fixture(scope="module")
def grass() -> gst.session.Grass:
    g = gst.session.Grass()
    return g


@pytest.fixture
def data_fixtures():
    module = pathlib.Path(__file__)
    data_fixtures = module.parent / "data_fixtures"
    return data_fixtures


@pytest.fixture
def tloc(request, data_fixtures):
    """
    Returns a Test Location from the `data_fixtures` directory.
    Must be used with `pytest.mark.parametrize(indirect=True)`.
    """
    return data_fixtures / "TestBase/Test4326"


class TestGrass(object):
    @pytest.mark.parametrize("attr", ["executable", "gisbase", "python_lib"])
    def test_grass_has_parameter(self, grass, attr):
        assert hasattr(grass, attr)


class TestSession(object):
    def test_environment_is_teared_down_cleanly(self, tloc, grass):
        orig_env = os.environ.copy()
        orig_sys_path = sys.path.copy()
        with gst.session.Session(tloc, grass=grass):
            session_env = os.environ.copy()
            session_sys_path = sys.path.copy()
            assert orig_env != session_env
            assert orig_sys_path != session_sys_path
        assert orig_sys_path == sys.path.copy()
        assert orig_env == os.environ.copy()

    def test_we_can_import_grass(self, grass, tloc):
        with gst.session.Session(tloc, grass=grass):
            import grass  # type: ignore
            import grass.script  # type: ignore

    @pytest.mark.parametrize(
        "env", ["GISRC", "GIS_LOCK", "GISBASE", "GRASS_PYTHON", "GRASS_ADDON_BASE"]
    )
    def test_grass_env_variables_are_being_setup_and_teared_down(
        self, tloc, grass, env
    ):
        assert os.environ.get(env) is None
        with gst.session.Session(tloc, grass=grass):
            assert os.environ.get(env) is not None
        assert os.environ.get(env) is None

    def test_session_is_active(self, tloc, grass):
        with gst.session.Session(tloc, grass=grass) as session:
            assert session.is_active is True
        assert session.is_active is False


@pytest.mark.parametrize(
    "env", ["GISRC", "GIS_LOCK", "GISBASE", "GRASS_PYTHON", "GRASS_ADDON_BASE"]
)
def test_decorator(tloc, grass, env):
    # Create the decorator. We need a different decorator per Location!
    grass_session = gst.session.Session(tloc, grass=grass)

    # Define the function that will run inside the GRASS session
    @grass_session
    def inside_grass_session():
        assert env in os.environ
        assert shutil.which("r.report")

    # run the tests
    assert env not in os.environ
    assert not shutil.which("r.report")
    inside_grass_session()
    assert env not in os.environ
    assert not shutil.which("r.report")
    with grass_session:
        assert env in os.environ
        assert shutil.which("r.report")
    assert env not in os.environ
    assert not shutil.which("r.report")
