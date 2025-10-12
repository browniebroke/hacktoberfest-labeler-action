"""Pytest configuration and fixtures."""

from types import SimpleNamespace

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def mock_repo(mocker: MockerFixture):
    """Create a mock Repository instance."""
    repo = mocker.MagicMock()
    repo.get_topics.return_value = []
    return repo


@pytest.fixture
def mock_label():
    """Create a mock Label instance."""
    return SimpleNamespace(
        name="hacktoberfest",
        color="ff6b6b",
        description="Hacktoberfest participation",
    )


@pytest.fixture
def mock_issue(mocker: MockerFixture):
    """Create a mock Issue instance."""
    issue = mocker.MagicMock()
    return issue
