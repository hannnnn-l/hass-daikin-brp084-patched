"""Shared fixtures."""

from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def hass_config_dir() -> str:
    """Use the repo root as HA config dir so custom_components/daikin is found."""
    for name in [m for m in sys.modules if m.split(".")[0] == "custom_components"]:
        del sys.modules[name]
    return str(REPO_ROOT)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Load custom_components/daikin instead of the core integration."""
    yield
