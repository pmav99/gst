import os
import sys

import pytest  # type: ignore

from gst.system_restore import system_restore


GIBBERISH = "GIBBERISH"


def test_sys_path_is_restored():
    orig = sys.path.copy()
    with system_restore():
        sys.path.append("/tmp")
    assert "/tmp" not in sys.path
    assert sys.path == orig


def test_sys_meta_path_is_restored():
    orig = sys.meta_path.copy()
    with system_restore():
        sys.meta_path.append(GIBBERISH)
    assert GIBBERISH not in sys.meta_path
    assert sys.meta_path == orig


def test_sys_path_hooks_is_restored():
    orig = sys.path_hooks.copy()
    with system_restore():
        sys.path_hooks.append(GIBBERISH)
    assert GIBBERISH not in sys.path_hooks
    assert sys.path_hooks == orig


def test_os_environ_is_restored():
    original = os.environ.copy()
    with system_restore():
        os.environ[GIBBERISH] = GIBBERISH
    assert GIBBERISH not in os.environ
    assert os.environ == original
