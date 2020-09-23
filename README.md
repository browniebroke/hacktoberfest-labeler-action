# Hacktoberfest Labeler Action

A Github Action to add labels based on other labels.

## Usage

A workflow you can run during the month of October to add the `hacktoberfest` label to all the issues flagged as `good first issue`:

```yaml
name: Hacktoberfest

on:
  schedule:
    - cron: "0 0 * 10 *"

jobs:
  example:
    runs-on: ubuntu-latest

    steps:
      - uses: browniebroke/hacktoberfest-labeler-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```
