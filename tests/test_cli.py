"""Tests for the hacktoberfest-labeler CLI."""

from github import UnknownObjectException
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from hacktoberfest_labeler.cli import (
    add_label,
    add_topic,
    app,
    get_or_create_label,
    remove_label,
    remove_topic,
)

runner = CliRunner()


class TestMain:
    """Tests for the main function."""

    def test_main_normal_mode(self, mocker: MockerFixture, mock_repo, mock_label):
        """Test main function in normal (non-revert) mode."""
        # Setup
        mock_github_class = mocker.patch(
            "hacktoberfest_labeler.cli.Github",
            autospec=True,
        )
        mock_github = mocker.MagicMock()
        mock_github_class.return_value = mock_github
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_label.return_value = mock_label
        mock_repo.get_issues.return_value = []
        mock_repo.get_topics.return_value = []

        # Execute
        result = runner.invoke(
            app,
            [
                "--github-token",
                "test_token",
                "--repository",
                "owner/repo",
                "--filter-label",
                "good first issue",
                "--edit-label-name",
                "hacktoberfest",
                "--edit-label-color",
                "ff6b6b",
                "--edit-label-description",
                "Hacktoberfest participation",
                "--no-revert",
            ],
        )

        # Verify
        assert result.exit_code == 0, (
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )
        mock_github_class.assert_called_once_with(login_or_token="test_token")  # noqa: S106
        mock_github.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_label.assert_called_once_with("hacktoberfest")
        mock_repo.get_issues.assert_called_once_with(
            state="open", labels=["good first issue"]
        )
        mock_repo.get_topics.assert_called_once()
        mock_repo.replace_topics.assert_called_once_with(["hacktoberfest"])

    def test_main_revert_mode(self, mocker: MockerFixture, mock_repo):
        """Test main function in revert mode."""
        # Setup
        mock_github_class = mocker.patch(
            "hacktoberfest_labeler.cli.Github", autospec=True
        )
        mock_github = mocker.MagicMock()
        mock_github_class.return_value = mock_github
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_issues.return_value = []
        mock_repo.get_topics.return_value = ["hacktoberfest", "python"]

        # Execute
        result = runner.invoke(
            app,
            [
                "--github-token",
                "test_token",
                "--repository",
                "owner/repo",
                "--filter-label",
                "good first issue",
                "--edit-label-name",
                "hacktoberfest",
                "--edit-label-color",
                "ff6b6b",
                "--edit-label-description",
                "Hacktoberfest participation",
                "--revert",
            ],
        )

        # Verify
        assert result.exit_code == 0
        mock_github_class.assert_called_once_with(login_or_token="test_token")  # noqa: S106
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

    def test_remove_label_multiple_issues(self, mocker: MockerFixture, mock_repo):
        """Test removing label from multiple issues."""
        issue1 = mocker.MagicMock()
        issue2 = mocker.MagicMock()
        issue3 = mocker.MagicMock()
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
        mock_repo.get_topics.return_value = [
            "python",
            "hacktoberfest",
            "github-actions",
        ]

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

        add_label(mock_repo, "good first issue", mock_label)

        mock_repo.get_issues.assert_called_once_with(
            state="open", labels=["good first issue"]
        )

    def test_add_label_single_issue(self, mock_repo, mock_label, mock_issue):
        """Test adding label to a single issue."""
        mock_repo.get_issues.return_value = [mock_issue]

        add_label(mock_repo, "good first issue", mock_label)

        mock_repo.get_issues.assert_called_once_with(
            state="open", labels=["good first issue"]
        )
        mock_issue.add_to_labels.assert_called_once_with(mock_label)

    def test_add_label_multiple_issues(
        self, mocker: MockerFixture, mock_repo, mock_label
    ):
        """Test adding label to multiple issues."""
        issue1 = mocker.MagicMock()
        issue2 = mocker.MagicMock()
        issue3 = mocker.MagicMock()
        mock_repo.get_issues.return_value = [issue1, issue2, issue3]

        add_label(mock_repo, "good first issue", mock_label)

        mock_repo.get_issues.assert_called_once_with(
            state="open", labels=["good first issue"]
        )
        issue1.add_to_labels.assert_called_once_with(mock_label)
        issue2.add_to_labels.assert_called_once_with(mock_label)
        issue3.add_to_labels.assert_called_once_with(mock_label)


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
        mock_repo.get_topics.return_value = [
            "python",
            "hacktoberfest",
            "github-actions",
        ]

        add_topic(mock_repo)

        mock_repo.get_topics.assert_called_once()
        mock_repo.replace_topics.assert_not_called()

    def test_add_topic_no_existing_topics(self, mock_repo):
        """Test adding topic when no topics exist."""
        mock_repo.get_topics.return_value = []

        add_topic(mock_repo)

        mock_repo.get_topics.assert_called_once()
        mock_repo.replace_topics.assert_called_once_with(["hacktoberfest"])
