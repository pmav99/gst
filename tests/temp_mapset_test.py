import pathlib

import pytest  # type: ignore

import gst


def test_temp_mapset(epsg4326):
    with epsg4326:
        import grass.pygrass.gis as ggis

        outer = ggis.Mapset()
        assert outer.name == "PERMANENT"
        assert outer.is_current
        with gst.utils.temp_mapset() as inner:
            assert not outer.is_current()
            assert inner.is_current()
            assert outer.gisdbase == inner.gisdbase
            assert outer.location == inner.location
            assert outer.name != inner.name
        assert outer.is_current()
        assert not inner.is_current()


def test_temp_mapset_cleanup(epsg4326):
    with epsg4326:
        import grass.pygrass.gis as ggis

        # Do cleanup
        with gst.utils.temp_mapset(cleanup=True) as inner:
            path = pathlib.Path(inner.path())
            assert path.exists()
        assert not path.exists()
        # Don't cleanup
        with gst.utils.temp_mapset(cleanup=False) as inner:
            path = pathlib.Path(inner.path())
            assert path.exists()
        assert path.exists()


def test_temp_mapset_mapset_name(epsg4326):
    with epsg4326:
        import grass.pygrass.gis as ggis

        mapset_name = "asdf"
        with gst.utils.temp_mapset(mapset_name=mapset_name) as inner:
            assert inner.name == mapset_name


def test_with_temp_mapset(epsg4326):
    with epsg4326:
        import grass.pygrass.gis as ggis

    mapset_name = "asdf"

    @epsg4326
    @gst.with_temp_mapset(mapset_name=mapset_name)
    def decorated_function():
        assert ggis.Mapset().name == mapset_name

    decorated_function()
