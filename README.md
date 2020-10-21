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
  example:
    runs-on: ubuntu-latest

    steps:
      - uses: browniebroke/hacktoberfest-labeler-action@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```
