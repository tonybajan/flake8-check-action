# Flake8 Check Action

A GitHub action to run [Flake8](https://flake8.readthedocs.io/en/latest/) against your code

## Features

* Configurable violations to fail on from the workflow YAML file
* Reports failures using the GitHub Checks API, so you get rich annotations in your pull request
* Plugins included: as well as reporting violations from [pycodestyle](https://pycodestyle.readthedocs.io/en/latest/) and [pyflakes](https://github.com/PyCQA/pyflakes), also optionally run the checks from [flake8-breakpoint](https://github.com/afonasev/flake8-breakpoint), [flake8-bugbear](https://github.com/PyCQA/flake8-bugbear) and [flake8-logging-format](https://github.com/globality-corp/flake8-logging-format)


## Configuration

Create or adapt your workflow file in `.github/workflows/` 

```yaml
on: push
name: Push
jobs:
  lint:
    name: Lint with Flake8
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: tonybajan/flake8-check-action@v1
      with:
        select: E3,E4,E5,E7,W6,F,B,G0
        maxlinelength: 100
        repotoken: ${{ secrets.GITHUB_TOKEN }}
```
