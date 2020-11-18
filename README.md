# Hacktoberfest Labeler Action

A Github Action to opt-in to Hacktoberfest every year.

## Usage

This workflow will be adding the `hacktoberfest` topic to your repo and label all the issues flagged as `good first issue` with the `hacktoberfest` label.

The workflow will behave differently if executed in October. You can run it once at the beginning of November to remove the `hacktoberfest` topic from your repo and un-label your issues.

```yaml
name: Hacktoberfest

on:
  schedule:
    # Run every day in October
    - cron: "0 0 * 10 *"
    # Run on the 1st of November to revert
    - cron: "0 13 1 11 *"

jobs:
  hacktoberfest:
    runs-on: ubuntu-latest

    steps:
      - uses: browniebroke/hacktoberfest-labeler-action@main
        with:
          github_token: ${{ secrets.GH_PAT }}
```

Note that the default `secrets.GITHUB_TOKEN` hasn't got [enough permissions][token-permissions], and cannot update the repository's topics. You should create a repo scoped  [personal access token][pat] instead.

[token-permissions]: https://docs.github.com/en/free-pro-team@latest/actions/reference/authentication-in-a-workflow#permissions-for-the-github_token
[pat]: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
