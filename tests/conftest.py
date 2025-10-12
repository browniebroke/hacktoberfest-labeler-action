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


@pytest.fixture
def mock_github(mocker: MockerFixture, mock_repo):
    """Create a mock Github instance with repository setup."""
    mock_github_class = mocker.patch(
        "hacktoberfest_labeler.cli.Github",
        autospec=True,
    )
    mock_github_instance = mocker.MagicMock()
    mock_github_class.return_value = mock_github_instance
    mock_github_instance.get_repo.return_value = mock_repo
    return mock_github_instance
