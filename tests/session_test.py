import os
import pathlib
import sys

import pytest

import gst
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
            pass
        assert orig_sys_path == sys.path.copy()
        assert orig_env == os.environ.copy()

    def test_we_can_import_grass(self, grass, tloc):
        with gst.session.Session(tloc, grass=grass):
            import grass
            import grass.script

    @pytest.mark.parametrize(
        "env", ["GISRC", "GIS_LOCK", "GISBASE", "GRASS_PYTHON", "GRASS_ADDON_BASE"]
    )
    def test_grass_env_variables_are_being_setup_and_teared_down(
        self, tloc, grass, env
    ):
        print(grass)
        print(type(grass))
        assert not os.environ.get(env)
        with gst.session.Session(tloc, grass=grass):
            assert os.environ.get(env)
        assert not os.environ.get(env)
