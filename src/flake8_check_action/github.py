import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from . import __version__
from .formatter import GitHubCheckFormatter

logger = logging.getLogger(__name__)


class GitHubCheckRun:
    def __init__(self, token: str, repo: str, sha: str, workspace: str, path: str):
        self.token = token

        self.repo = repo
        self.sha = sha
        self.workspace = workspace
        self.path = path

        self.session = requests.sessions.Session()
        self.session.headers['Accept'] = 'application/vnd.github.antiope-preview+json'
        self.session.headers['Authorization'] = f'Bearer {self.token}'
        self.session.headers['Content-Type'] = 'application/json'
        self.session.headers['User-Agent'] = f'flake8-check-action/{__version__}'

        check_run = {
            'name': 'Flake8 violations',
            'head_sha': self.sha,
            'status': 'in_progress',
            'started_at': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
            'output': {
                'title': 'Flake8 violations',
                'summary': '',
            }
        }

        url = f'https://api.github.com/repos/{self.repo}/check-runs'
        logger.info('Create check run: %s', check_run)
        if self.token:
            response = self.session.post(url, data=json.dumps(check_run))
            logger.info('GitHub Response: %s', response.content)
            response.raise_for_status()
            response_data = response.json()
            self.check_run_url = f'{url}/{response_data["id"]}'

    def _format_annotations(self, formatter: GitHubCheckFormatter) -> list[dict[str, Any]]:
        annotations = []
        for violation in formatter.violations_outstanding:
            filename = Path(violation.filename)
            if filename.is_absolute():
                filename = filename.relative_to(self.workspace)
            annotations.append({
                'path': str(filename),
                'start_line': violation.line_number,
                'end_line': violation.line_number,
                'start_column': violation.column_number,
                'end_column': violation.column_number,
                'annotation_level': 'failure' if violation.code.startswith('F') else 'warning',
                'message': violation.text,
                'title': violation.code,
            })
        return annotations

    def send_outstanding_annotations(self, formatter: GitHubCheckFormatter) -> None:
        check_data = {
            'output': {
                'annotations': self._format_annotations(formatter)
            }
        }

        logger.info('Update check run: %s', check_data)
        if self.token:
            response = self.session.patch(self.check_run_url, data=json.dumps(check_data))
            logger.info('GitHub Response: %s', response.content)
            response.raise_for_status()

    def complete(self, formatter: GitHubCheckFormatter, summary: str) -> None:
        check_data = {
            'output': {
                'title': 'Flake8 violations',
                'summary': summary,
                'annotations': self._format_annotations(formatter),
            },
            'status': 'completed',
            'completed_at': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
            'conclusion': 'failure' if formatter.violations_seen else 'success',
        }

        logger.info('Update check run: %s', check_data)
        if self.token:
            response = self.session.patch(self.check_run_url, data=json.dumps(check_data))
            logger.info('GitHub Response: %s', response.content)
            response.raise_for_status()
