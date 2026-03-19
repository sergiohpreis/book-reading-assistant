from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def tmp_library(tmp_path: Path) -> Path:
    library_dir = tmp_path / "library"
    library_dir.mkdir()
    return library_dir
