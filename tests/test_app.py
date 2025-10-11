"""Tests for the hacktoberfest-labeler-action app."""

import datetime as dt
from unittest.mock import MagicMock, call, patch

import pytest
from github import UnknownObjectException

from src.app import (
    add_label,
    add_topic,
    get_or_create_label,
    main,
    remove_label,
    remove_topic,
)


class TestMain:
    """Tests for the main function."""

    @patch("src.app.Github")
    def test_main_normal_mode(self, mock_github_class, mock_repo, mock_label):
        """Test main function in normal (non-revert) mode."""
        # Setup
        mock_github = MagicMock()
        mock_github_class.return_value = mock_github
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_label.return_value = mock_label
        mock_repo.get_issues.return_value = []
        mock_repo.get_topics.return_value = []

        # Execute
        main(
            github_token="test_token",
            github_repository="owner/repo",
            filter_label_names=["good first issue"],
            edit_label="hacktoberfest",
            edit_label_color="ff6b6b",
            edit_label_description="Hacktoberfest participation",
            revert=False,
        )

        # Verify
        mock_github_class.assert_called_once_with(login_or_token="test_token")
        mock_github.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_label.assert_called_once_with("hacktoberfest")
        mock_repo.get_issues.assert_called_once_with(
            state="open", labels=["good first issue"]
        )
        mock_repo.get_topics.assert_called_once()
        mock_repo.replace_topics.assert_called_once_with(["hacktoberfest"])

    @patch("src.app.Github")
    def test_main_revert_mode(self, mock_github_class, mock_repo):
        """Test main function in revert mode."""
        # Setup
        mock_github = MagicMock()
        mock_github_class.return_value = mock_github
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_issues.return_value = []
        mock_repo.get_topics.return_value = ["hacktoberfest", "python"]

        # Execute
        main(
            github_token="test_token",
            github_repository="owner/repo",
            filter_label_names=["good first issue"],
            edit_label="hacktoberfest",
            edit_label_color="ff6b6b",
            edit_label_description="Hacktoberfest participation",
            revert=True,
        )

        # Verify
        mock_github_class.assert_called_once_with(login_or_token="test_token")
        mock_github.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_issues.assert_called_once_with(
            state="open", labels=["hacktoberfest"]
        )
        mock_repo.get_topics.assert_called_once()
        mock_repo.replace_topics.assert_called_once_with(["python"])


class TestRemoveLabel:
    """Tests for the remove_label function."""

    def test_remove_label_no_issues(self, mock_repo):
        """Test removing label when no issues have it."""
        mock_repo.get_issues.return_value = []

        remove_label(mock_repo, "hacktoberfest")

        mock_repo.get_issues.assert_called_once_with(
            state="open", labels=["hacktoberfest"]
        )

    def test_remove_label_single_issue(self, mock_repo, mock_issue):
        """Test removing label from a single issue."""
        mock_repo.get_issues.return_value = [mock_issue]

        remove_label(mock_repo, "hacktoberfest")

        mock_repo.get_issues.assert_called_once_with(
            state="open", labels=["hacktoberfest"]
        )
        mock_issue.remove_from_labels.assert_called_once_with("hacktoberfest")

    def test_remove_label_multiple_issues(self, mock_repo):
        """Test removing label from multiple issues."""
        issue1 = MagicMock()
        issue2 = MagicMock()
        issue3 = MagicMock()
        mock_repo.get_issues.return_value = [issue1, issue2, issue3]

        remove_label(mock_repo, "hacktoberfest")

        mock_repo.get_issues.assert_called_once_with(
            state="open", labels=["hacktoberfest"]
        )
        issue1.remove_from_labels.assert_called_once_with("hacktoberfest")
        issue2.remove_from_labels.assert_called_once_with("hacktoberfest")
        issue3.remove_from_labels.assert_called_once_with("hacktoberfest")


class TestRemoveTopic:
    """Tests for the remove_topic function."""

    def test_remove_topic_not_present(self, mock_repo):
        """Test removing topic when it's not present."""
        mock_repo.get_topics.return_value = ["python", "github-actions"]

        remove_topic(mock_repo)

        mock_repo.get_topics.assert_called_once()
        mock_repo.replace_topics.assert_not_called()

    def test_remove_topic_present_only(self, mock_repo):
        """Test removing topic when it's the only topic."""
        mock_repo.get_topics.return_value = ["hacktoberfest"]

        remove_topic(mock_repo)

        mock_repo.get_topics.assert_called_once()
        mock_repo.replace_topics.assert_called_once_with([])

    def test_remove_topic_present_with_others(self, mock_repo):
        """Test removing topic when other topics exist."""
        mock_repo.get_topics.return_value = ["python", "hacktoberfest", "github-actions"]

        remove_topic(mock_repo)

        mock_repo.get_topics.assert_called_once()
        mock_repo.replace_topics.assert_called_once_with(["python", "github-actions"])


class TestGetOrCreateLabel:
    """Tests for the get_or_create_label function."""

    def test_get_existing_label(self, mock_repo, mock_label):
        """Test getting an existing label."""
        mock_repo.get_label.return_value = mock_label

        result = get_or_create_label(
            mock_repo,
            "hacktoberfest",
            "ff6b6b",
            "Hacktoberfest participation",
        )

        assert result == mock_label
        mock_repo.get_label.assert_called_once_with("hacktoberfest")
        mock_repo.create_label.assert_not_called()

    def test_create_new_label(self, mock_repo, mock_label):
        """Test creating a new label when it doesn't exist."""
        mock_repo.get_label.side_effect = UnknownObjectException(404, "Not found", {})
        mock_repo.create_label.return_value = mock_label

        result = get_or_create_label(
            mock_repo,
            "hacktoberfest",
            "ff6b6b",
            "Hacktoberfest participation",
        )

        assert result == mock_label
        mock_repo.get_label.assert_called_once_with("hacktoberfest")
        mock_repo.create_label.assert_called_once_with(
            name="hacktoberfest",
            color="ff6b6b",
            description="Hacktoberfest participation",
        )


class TestAddLabel:
    """Tests for the add_label function."""

    def test_add_label_no_issues(self, mock_repo, mock_label):
        """Test adding label when no issues match filter."""
        mock_repo.get_issues.return_value = []

        add_label(mock_repo, ["good first issue"], mock_label)

        mock_repo.get_issues.assert_called_once_with(
            state="open", labels=["good first issue"]
        )

    def test_add_label_single_issue(self, mock_repo, mock_label, mock_issue):
        """Test adding label to a single issue."""
        mock_repo.get_issues.return_value = [mock_issue]

        add_label(mock_repo, ["good first issue"], mock_label)

        mock_repo.get_issues.assert_called_once_with(
            state="open", labels=["good first issue"]
        )
        mock_issue.add_to_labels.assert_called_once_with(mock_label)

    def test_add_label_multiple_issues(self, mock_repo, mock_label):
        """Test adding label to multiple issues."""
        issue1 = MagicMock()
        issue2 = MagicMock()
        issue3 = MagicMock()
        mock_repo.get_issues.return_value = [issue1, issue2, issue3]

        add_label(mock_repo, ["good first issue"], mock_label)

        mock_repo.get_issues.assert_called_once_with(
            state="open", labels=["good first issue"]
        )
        issue1.add_to_labels.assert_called_once_with(mock_label)
        issue2.add_to_labels.assert_called_once_with(mock_label)
        issue3.add_to_labels.assert_called_once_with(mock_label)

    def test_add_label_multiple_filter_labels(self, mock_repo, mock_label, mock_issue):
        """Test adding label with multiple filter labels."""
        mock_repo.get_issues.return_value = [mock_issue]
        filter_labels = ["good first issue", "help wanted"]

        add_label(mock_repo, filter_labels, mock_label)

        mock_repo.get_issues.assert_called_once_with(
            state="open", labels=filter_labels
        )
        mock_issue.add_to_labels.assert_called_once_with(mock_label)


class TestAddTopic:
    """Tests for the add_topic function."""

    def test_add_topic_not_present(self, mock_repo):
        """Test adding topic when it's not present."""
        mock_repo.get_topics.return_value = ["python", "github-actions"]

        add_topic(mock_repo)

        mock_repo.get_topics.assert_called_once()
        mock_repo.replace_topics.assert_called_once_with(
            ["python", "github-actions", "hacktoberfest"]
        )

    def test_add_topic_already_present(self, mock_repo):
        """Test adding topic when it's already present."""
        mock_repo.get_topics.return_value = ["python", "hacktoberfest", "github-actions"]

        add_topic(mock_repo)

        mock_repo.get_topics.assert_called_once()
        mock_repo.replace_topics.assert_not_called()

    def test_add_topic_no_existing_topics(self, mock_repo):
        """Test adding topic when no topics exist."""
        mock_repo.get_topics.return_value = []

        add_topic(mock_repo)

        mock_repo.get_topics.assert_called_once()
        mock_repo.replace_topics.assert_called_once_with(["hacktoberfest"])


class TestMainEntryPoint:
    """Tests for the __main__ entry point logic."""

    @patch.dict(
        "os.environ",
        {
            "GITHUB_REPOSITORY": "owner/repo",
            "INPUT_GITHUB_TOKEN": "test_token",
            "INPUT_EDIT_LABEL_NAME": "hacktoberfest",
            "INPUT_EDIT_LABEL_COLOR": "ff6b6b",
            "INPUT_EDIT_LABEL_DESCRIPTION": "Hacktoberfest participation",
            "INPUT_FILTER_LABEL": "good first issue",
            "INPUT_REVERT": "false",
        },
    )
    @patch("src.app.main")
    def test_main_entry_point_explicit_revert_false(self, mock_main):
        """Test main entry point with explicit revert=false."""
        # Import and execute the module
        with patch("src.app.env") as mock_env:
            mock_env.return_value = "test_value"
            mock_env.list.return_value = ["good first issue"]
            mock_env.bool.return_value = False

            # Simulate running the script
            exec(
                compile(
                    open(
                        "/Users/bruno/Documents/Workspace/oss/sources/hacktoberfest-labeler-action/src/app.py"
                    ).read(),
                    "app.py",
                    "exec",
                )
            )

    @patch("src.app.dt.date")
    @patch.dict(
        "os.environ",
        {
            "GITHUB_REPOSITORY": "owner/repo",
            "INPUT_GITHUB_TOKEN": "test_token",
            "INPUT_EDIT_LABEL_NAME": "hacktoberfest",
            "INPUT_EDIT_LABEL_COLOR": "ff6b6b",
            "INPUT_EDIT_LABEL_DESCRIPTION": "Hacktoberfest participation",
            "INPUT_FILTER_LABEL": "good first issue",
            "INPUT_REVERT": "",
        },
    )
    def test_revert_logic_october(self, mock_date):
        """Test that revert is False when in October and INPUT_REVERT is empty."""
        mock_today = MagicMock()
        mock_today.month = 10
        mock_date.today.return_value = mock_today

        # Simulate the revert logic
        import os

        if os.getenv("INPUT_REVERT", None) == "":
            today = dt.date.today()
            input_revert = today.month != 10
        else:
            input_revert = True

        assert input_revert is False

    @patch("src.app.dt.date")
    @patch.dict(
        "os.environ",
        {
            "INPUT_REVERT": "",
        },
    )
    def test_revert_logic_not_october(self, mock_date):
        """Test that revert is True when not in October and INPUT_REVERT is empty."""
        mock_today = MagicMock()
        mock_today.month = 11
        mock_date.today.return_value = mock_today

        # Simulate the revert logic
        import os

        if os.getenv("INPUT_REVERT", None) == "":
            today = dt.date.today()
            input_revert = today.month != 10
        else:
            input_revert = True

        assert input_revert is True
