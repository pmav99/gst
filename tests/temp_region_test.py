import pytest  # type: ignore

import gst.session
import gst.utils


def test_temp_region_can_only_be_used_inside_a_grass_session():
    with pytest.raises(ValueError) as exc:
        with gst.utils.temp_region():
            pass
    assert "inside a GRASS session" in str(exc)


def test_temp_region_without_map(epsg4326):
    with epsg4326:
        from grass.pygrass.gis import Region

        initial = Region()
        assert initial.rows == 1
        assert initial.cols == 1
        with gst.utils.temp_region() as inner:
            assert initial.rows == inner.rows
            assert initial.cols == inner.cols
            inner.rows = 1000
            inner.cols = 1000
            inner.write()
        current = Region()
        assert current.rows != inner.rows
        assert current.cols != inner.cols
        assert current.rows == initial.rows
        assert current.cols == initial.cols


@pytest.mark.parametrize(
    "map_name,size", [pytest.param("sq2_000", 2), pytest.param("sq5_000", 5)]
)
def test_temp_region_with_a_raster(epsg4326, map_name, size):
    with epsg4326:
        from grass.pygrass.gis import Region

        initial = Region()
        assert initial.rows == 1
        assert initial.cols == 1
        with gst.utils.temp_region(raster=map_name) as inner:
            assert initial.rows != inner.rows
            assert initial.cols != inner.cols
            assert inner.rows == size
            assert inner.cols == size
        current = Region()
        assert current.rows != inner.rows
        assert current.cols != inner.cols
        assert current.rows == initial.rows
        assert current.cols == initial.cols


def test_with_temp_region(epsg4326):
    with epsg4326:
        import grass.pygrass.gis as ggis

    @epsg4326
    @gst.with_temp_region()
    def decorated():
        region = ggis.Region()
        assert region.rows == 1
        region.rows = 1000
        region.write()

    with epsg4326:
        assert ggis.Region().rows == 1
    decorated()
    with epsg4326:
        assert ggis.Region().rows == 1
