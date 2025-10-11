"""Pytest configuration and fixtures."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_github():
    """Create a mock Github instance."""
    return MagicMock()


@pytest.fixture
def mock_repo():
    """Create a mock Repository instance."""
    repo = MagicMock()
    repo.get_topics.return_value = []
    return repo


@pytest.fixture
def mock_label():
    """Create a mock Label instance."""
    label = MagicMock()
    label.name = "hacktoberfest"
    label.color = "ff6b6b"
    label.description = "Hacktoberfest participation"
    return label


@pytest.fixture
def mock_issue():
    """Create a mock Issue instance."""
    issue = MagicMock()
    return issue
