"""Shared fixtures.

The whole suite runs against a **small synthetic control world** built into a
temporary directory. No test reads the repository's real database trees, and no
test requires network access.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from src.core.configuration import load_config


@pytest.fixture(scope="session")
def fixture_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def small_config(tmp_path_factory):
    """A two-year null control world in a throwaway database root."""
    from src.ingestion.synthetic_control import ControlSpec, build_dataset

    root = tmp_path_factory.mktemp("sm_intel_db")
    config = load_config(dataset="synthetic_null", database_root=root)
    spec = ControlSpec(
        name="synthetic_null",
        start=date(2019, 1, 1),
        end=date(2020, 12, 31),
        open_persistence=0.0,
        close_persistence=0.0,
        marginal_tilt=0.0,
        cross_market_strength=0.0,
        seed=1234,
    )
    build_dataset(config, spec)
    return config


@pytest.fixture(scope="session")
def small_signal_config(tmp_path_factory):
    """A short signal world: planted dependence, for positive-control tests."""
    from src.ingestion.synthetic_control import ControlSpec, build_dataset

    root = tmp_path_factory.mktemp("sm_intel_signal")
    config = load_config(dataset="synthetic_signal", database_root=root)
    spec = ControlSpec(
        name="synthetic_signal",
        start=date(2019, 1, 1),
        end=date(2021, 12, 31),
        open_persistence=0.30,
        close_persistence=0.22,
        marginal_tilt=0.0,
        cross_market_strength=0.18,
        seed=4321,
    )
    build_dataset(config, spec)
    return config
