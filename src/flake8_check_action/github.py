import json
import logging
from datetime import datetime

import requests

from . import __version__
from .formatter import GitHubCheckFormatter

logger = logging.getLogger(__name__)


class GitHubCheckRun(object):
    def __init__(self, token: str, repo: str, sha: str, path: str):
        self.token = token

        self.repo = repo
        self.sha = sha
        self.path = path

        self.session = requests.sessions.Session()
        self.session.headers['Accept'] = 'application/vnd.github.antiope-preview+json'
        self.session.headers['Authorization'] = f'Bearer {self.token}'
        self.session.headers['Content-Type'] = 'application/json'
        self.session.headers['User-Agent'] = f'flake8-check-action/{__version__}'

        check_run = {
            'name': 'Flake8 checks',
            'head_sha': self.sha,
            'status': 'in_progress',
            'started_at': datetime.utcnow().isoformat()
        }

        url = f'https://api.github.com/repos/{self.repo}/check-runs'
        if self.token:
            response = self.session.post(url, data=json.dumps(check_run))
            response.raise_for_status()
            response_data = response.json()
            self.check_run_url = f'{url}/{response_data["id"]}'
        else:
            logger.info('Create check run: %s', check_run)

    def _format_annotations(self, formatter):
        annotations = []
        for violation in formatter.violations_outstanding:
            annotations.append({
                'path': violation.filename,
                'start_line': violation.line_number,
                'end_line': violation.line_number,
                'start_column': violation.column_number,
                'end_column': violation.column_number,
                'annotation_level': 'failure' if violation.code.startswith('F') else 'warning',
                'message': violation.text,
                'title': violation.code,
            })

    def send_outstanding_annotations(self, formatter: GitHubCheckFormatter):
        check_data = {
            'output': {
                'summary': 'No violations' if not formatter.violations_seen else 'Violations found',
                'annotations': self._format_annotations(formatter)
            }
        }

        if self.token:
            self.session.patch(self.check_run_url, data=json.dumps(check_data))
        else:
            logger.info('Update check run: %s', check_data)

    def complete(self, formatter: GitHubCheckFormatter, summary: str):
        check_data = {
            'output': {
                'summary': summary,
                'annotations': self._format_annotations(formatter),
                'completed_at': datetime.utcnow().isoformat(),
                'conclusion': 'failure' if formatter.violations_seen else 'success'
            }
        }

        if self.token:
            self.session.patch(self.check_run_url, data=json.dumps(check_data))
        else:
            logger.info('Complete check run: %s', check_data)

