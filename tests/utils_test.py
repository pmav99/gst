import os
import pathlib

import pytest  # type: ignore

import gst.session
import gst.utils
from . import param_test_locations
from gst.utils import resolve_grass_executable


class TestResolveGrassExecutable(object):

    # since on the dev environment, we probably already have $GST_GRASS_EXECUTABLE in
    # our $PATH we will monkeypatch os.environ before each test to be sure that it is
    # undefined and restore its value on teardown
    @pytest.fixture(autouse=True)
    def patch_os_environ(self):
        original = os.environ.get("GST_GRASS_EXECUTABLE", "")
        os.environ.pop("GST_GRASS_EXECUTABLE", None)
        yield
        os.environ["GST_GRASS_EXECUTABLE"] = original

    @pytest.mark.parametrize("path", ["/zzz", "/home", "/etc/fstab"])
    def test_path_is_specified_but_not_an_executable_raises(self, path):
        with pytest.raises(ValueError) as exc:
            resolve_grass_executable(path)
        assert f"not: {path}" in str(exc)

    @pytest.mark.parametrize("path", ["/bin/ls", pathlib.Path("/bin/ls")])
    def test_path_is_specified_as_an_executable_OK(self, path):
        grass = resolve_grass_executable(path)
        assert grass == pathlib.Path(path)

    @pytest.mark.parametrize("path", ["/zzz", "/home", "/etc/fstab"])
    def test_gst_env_is_set_but_not_an_executable_raises(self, path):
        os.environ["GST_GRASS_EXECUTABLE"] = path
        with pytest.raises(ValueError) as exc:
            resolve_grass_executable()
        assert f"not: {path}" in str(exc)
        assert "GST_GRASS_EXECUTABLE" in str(exc)

    def test_gst_env_is_set_as_an_executable_OK(self):
        path = "/bin/ls"
        grass = resolve_grass_executable(path)
        assert grass == pathlib.Path(path)

    def test_grass_is_non_resolvable_raises(self):
        with pytest.raises(ValueError) as exc:
            resolve_grass_executable()
        assert "GST_GRASS_EXECUTABLE" in str(exc)


_RETURN_VALUE = "return value"


@gst.utils.require_grass
def decorated_function():
    import grass.pygrass.gis

    return _RETURN_VALUE


def test_require_grass_raises_when_called_out_of_session():
    with pytest.raises(ValueError) as exc:
        decorated_function()
    assert "<decorated_function>" in str(exc)


@param_test_locations
def test_require_grass_works_when_called_in_session(grass_bin, loc):
    with grass_bin.session(loc):
        assert decorated_function() == _RETURN_VALUE
