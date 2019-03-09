import os
import sys
from typing import Dict
from typing import List

import dataclasses
import decorator  # type: ignore


@dataclasses.dataclass(frozen=True)
class SystemState:
    """Class for saving the state of the system"""

    environ: Dict[str, str]
    meta_path: List
    path: List[str]
    path_hooks: List


def save_system_state() -> SystemState:
    """Return the system's state as a `SystemState` object"""
    state: SystemState = SystemState(
        environ=os.environ.copy(),
        meta_path=sys.meta_path.copy(),
        path=sys.path.copy(),
        path_hooks=sys.path_hooks.copy(),
    )
    return state


def restore_system_state(state: SystemState) -> None:
    """Restore the system to the given `state`"""
    os.environ.clear()
    os.environ.update(state.environ)
    sys.meta_path = state.meta_path
    sys.path = state.path
    sys.path_hooks = state.path_hooks


@decorator.contextmanager
def system_restore():
    state: SystemState = save_system_state()
    yield
    restore_system_state(state)
