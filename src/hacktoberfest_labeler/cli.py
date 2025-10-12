import datetime as dt
from typing import Annotated

import typer
from github import Github, UnknownObjectException
from github.Label import Label
from github.Repository import Repository

app = typer.Typer(help="A CLI tool to automate Hacktoberfest labeling")


@app.command()
def main(
    github_token: Annotated[
        str,
        typer.Option(
            "--github-token",
            "-t",
            envvar="GITHUB_TOKEN",
            help="GitHub token for authentication",
        ),
    ],
    github_repository: Annotated[
        str | None,
        typer.Option(
            "--repository",
            "-r",
            envvar="GITHUB_REPOSITORY",
            help="Repository in format owner/repo",
        ),
    ] = None,
    filter_label: Annotated[
        list[str],
        typer.Option(
            "--filter-label",
            "-f",
            help="Label(s) to use for filtering issues",
        ),
    ] = ["good first issue"],  # noqa: B006
    edit_label_name: Annotated[
        str,
        typer.Option(
            "--edit-label-name",
            "-n",
            help="The label name to edit",
        ),
    ] = "hacktoberfest",
    edit_label_color: Annotated[
        str,
        typer.Option(
            "--edit-label-color",
            "-c",
            help="The label color (hex without #)",
        ),
    ] = "ffa663",
    edit_label_description: Annotated[
        str,
        typer.Option(
            "--edit-label-description",
            "-d",
            help="The label description",
        ),
    ] = "Good issues for Hacktoberfest",
    revert: Annotated[
        bool | None,
        typer.Option(
            "--revert/--no-revert",
            help=(
                "Remove label instead of adding it. If not specified, "
                "auto-revert when not in October"
            ),
        ),
    ] = None,
) -> None:
    """
    Automate Hacktoberfest labeling for GitHub repositories.

    This tool will:
    - Create or update the hacktoberfest label
    - Add it to issues with the filter label(s)
    - Add the hacktoberfest topic to the repository

    Or revert these changes if --revert is specified or if it's not October.
    """
    if github_repository is None:
        typer.echo("Error: --repository is required", err=True)
        raise typer.Exit(1)

    # Auto-revert if not in October and revert not explicitly set
    if revert is None:
        today = dt.date.today()
        revert = today.month != 10

    gh = Github(login_or_token=github_token)
    repo = gh.get_repo(github_repository)

    if revert:
        typer.echo(f"Reverting Hacktoberfest changes for {github_repository}...")
        remove_label(repo, edit_label_name)
        remove_topic(repo)
        typer.echo("✓ Reverted successfully")
    else:
        typer.echo(f"Applying Hacktoberfest labels to {github_repository}...")
        label_to_add = get_or_create_label(
            repo,
            edit_label_name,
            edit_label_color,
            edit_label_description,
        )
        add_label(repo, filter_label, label_to_add)
        add_topic(repo)
        typer.echo("✓ Applied successfully")


def remove_label(repo: Repository, edit_label: str):
    """Remove label from all issues with it."""
    issues_list = repo.get_issues(state="open", labels=[edit_label])
    for issue in issues_list:
        issue.remove_from_labels(edit_label)


def remove_topic(repo: Repository):
    """Remove hacktoberfest topic from repo."""
    topics_list = repo.get_topics()
    if "hacktoberfest" in topics_list:
        topics_list = [t for t in topics_list if t != "hacktoberfest"]
        repo.replace_topics(topics_list)


def get_or_create_label(
    repo: Repository,
    edit_label: str,
    edit_label_color: str,
    edit_label_description: str,
) -> Label:
    """Get the Label object or create it with given features."""
    try:
        label_to_add = repo.get_label(edit_label)
    except UnknownObjectException:
        label_to_add = repo.create_label(
            name=edit_label,
            color=edit_label_color,
            description=edit_label_description,
        )
    return label_to_add


def add_label(repo: Repository, filter_label_names: list[str], label_to_add: Label):
    """Add given label to all issues labeled with filter label."""
    issues_list = repo.get_issues(state="open", labels=filter_label_names)
    for issue in issues_list:
        issue.add_to_labels(label_to_add)


def add_topic(repo: Repository):
    """Add hacktoberfest topic to the repo."""
    topics_list = repo.get_topics()
    if "hacktoberfest" not in topics_list:
        topics_list.append("hacktoberfest")
        repo.replace_topics(topics_list)
