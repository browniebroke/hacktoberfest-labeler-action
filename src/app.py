import os
from typing import List

from environs import Env
from github import Github, UnknownObjectException
from github.Label import Label
from github.Repository import Repository

env = Env()


def main(
    github_token: str,
    github_repository: str,
    filter_label_names: List[str],
    edit_label: str,
    edit_label_color: str,
    edit_label_description: str,
    revert: bool = False,
) -> None:
    """
    Script entry point.

    :param github_token: Github token.
    :param github_repository: The owner and repository name (octocat/Hello-World).
    :param filter_label_names: The label used to filter issues.
    :param edit_label: The label to be edited.
    :param edit_label_color: The color of label to be edited.
    :param edit_label_description: The description label to be edited.
    :param revert: Remove label instead of adding it.
    """

    gh = Github(login_or_token=github_token)
    repo = gh.get_repo(github_repository)
    if revert:
        remove_label(repo, edit_label)
    else:
        label_to_add = get_or_create_label(
            repo,
            edit_label,
            edit_label_color,
            edit_label_description,
        )
        add_label(repo, filter_label_names, label_to_add)


def remove_label(repo: Repository, edit_label: str):
    """Remove label from all issues with it."""
    issues_list = repo.get_issues(state="open", labels=[edit_label])
    for issue in issues_list:
        issue.remove_from_labels(edit_label)


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


def add_label(repo: Repository, filter_label_names: List[str], label_to_add: Label):
    """Add given label to all issues labeled with filter label."""
    issues_list = repo.get_issues(state="open", labels=filter_label_names)
    for issue in issues_list:
        issue.add_to_labels(label_to_add)


if __name__ == "__main__":
    env = Env()
    env.read_env()
    gh_repository = env("GITHUB_REPOSITORY")
    gh_token = env("INPUT_GITHUB_TOKEN")
    input_label_name = env("INPUT_EDIT_LABEL_NAME")
    input_label_color = env("INPUT_EDIT_LABEL_COLOR")
    input_label_description = env("INPUT_EDIT_LABEL_DESCRIPTION")
    input_filter_labels = env.list("INPUT_FILTER_LABEL")

    # In case it's set to an empty string, use default value
    if os.getenv("INPUT_REVERT", None) == "":
        input_revert = False
    else:
        input_revert = env.bool("INPUT_REVERT")

    main(
        gh_token,
        gh_repository,
        input_filter_labels,
        input_label_name,
        input_label_color,
        input_label_description,
        input_revert,
    )
