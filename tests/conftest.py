import pathlib

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
