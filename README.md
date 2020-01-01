# Flake8 Check Action

A GitHub action to run [Flake8](https://flake8.readthedocs.io/en/latest/) against your code

## Features

* Configure path and relevant violations from the workflow YAML file
* Reports failures using the GitHub Checks API for rich annotations in your pull request
* Plugins included: as well as reporting violations from [pycodestyle](https://pycodestyle.readthedocs.io/en/latest/) and [pyflakes](https://github.com/PyCQA/pyflakes), also optionally run the checks from [flake8-breakpoint](https://github.com/afonasev/flake8-breakpoint), [flake8-bugbear](https://github.com/PyCQA/flake8-bugbear) and [flake8-logging-format](https://github.com/globality-corp/flake8-logging-format). Enable them by selecting their error prefixes.


## Configuration

Create or adapt your workflow file in `.github/workflows/` to run `tonybajan/flake8-check-action` after `actions/checkout`.

```yaml
on: push
name: Push
jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: tonybajan/flake8-check-action@v1
      with:
        select: E3,E4,E5,E7,W6,F,B,G0
        maxlinelength: 100
        repotoken: ${{ secrets.GITHUB_TOKEN }}
```

### Parameters

| Parameter name  | Required  |  Description |
|---------------|:---:|---|
| `repotoken`     | ✓ |  The token to use to report GitHub Checks. Should be set to `${{ secrets.GITHUB_TOKEN }}`, which is automatically set by GitHub Actions.  |
| `path`          |   |  The path to check. Defaults to the whole repo. |
| `select`        |   |  A comma separated list of violations (or violation prefixes) that should fail the build. Defaults to `F`. |
| `ignore`        |   | A comma separated list of violations (or violation prefixes) to ignore. Nothing is ignored by default. |
| `maxlinelength` |   | The maximum line length for pycodestyle violation E501. Defaults to 79. |
