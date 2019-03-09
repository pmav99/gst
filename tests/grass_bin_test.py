import pytest  # type: ignore

import gst


@pytest.mark.parametrize("attr", ["executable", "gisbase", "python_lib"])
def test_grass_has_attribute(grass, attr):
    assert hasattr(grass, attr)
