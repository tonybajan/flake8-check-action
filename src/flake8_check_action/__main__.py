import logging
import os

from flake8.api.legacy import get_style_guide
from flake8.utils import parse_comma_separated_list

from .github import GitHubCheckRun

logger = logging.getLogger(__name__)


def run_check() -> None:
    default_select = 'F'
    github_token = os.getenv('INPUT_REPOTOKEN')
    if not github_token:
        logger.warning('No GitHub token found, check will not be reported')

    sha = os.getenv('GITHUB_SHA')
    path = os.getenv('INPUT_PATH') or os.getenv('GITHUB_WORKSPACE') or '.'
    repo = os.getenv('GITHUB_REPOSITORY')
    check_run = GitHubCheckRun(github_token, repo, sha, path)

    select = parse_comma_separated_list(os.getenv('INPUT_SELECT', default_select))
    ignore = parse_comma_separated_list(os.getenv('INPUT_IGNORE', ''))
    line_length = 79
    try:
        line_length = int(os.getenv('INPUT_MAXLINELENGTH') or line_length)
    except ValueError:
        pass

    style_guide = get_style_guide(
        select=select,
        ignore=ignore,
        format='github-check-formatter',
        max_line_length=line_length
    )
    formatter = style_guide._application.formatter
    formatter.check_run = check_run
    report = style_guide.check_files(paths=[path])

    if not formatter.violations_seen:
        summary = '*No violations*'
    else:
        summary = '*Violations were found*\n'
        for stat in report.get_statistics(''):
            summary += f'* {stat}\n'

    check_run.complete(formatter, summary=summary)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_check()
