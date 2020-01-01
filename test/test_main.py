import json
from unittest.mock import patch, ANY

import pytest
from flake8_check_action.__main__ import run_check


@pytest.fixture(autouse=True)
def environment(monkeypatch):
    monkeypatch.setenv('INPUT_REPOTOKEN', 'SECRET')
    monkeypatch.setenv('INPUT_PATH', 'test')
    monkeypatch.setenv('GITHUB_SHA', 'abcde')
    monkeypatch.setenv('GITHUB_REPOSITORY', 'tonybajan/flake8-check-action')


def test_main():

    with patch('flake8_check_action.github.requests.sessions.Session') as mock_session:
        mock_session.return_value.post.return_value.json.return_value = {
            'id': 123,
        }
        run_check()

    mock_session.return_value.post.assert_called_once_with(
        'https://api.github.com/repos/tonybajan/flake8-check-action/check-runs',
        data=ANY
    )
    data = json.loads(mock_session.return_value.post.mock_calls[0].kwargs['data'])
    assert data['name'] == 'Flake8 violations'
    assert data['head_sha'] == 'abcde'
    assert data['status'] == 'in_progress'

    mock_session.return_value.patch.assert_called_once_with(
        'https://api.github.com/repos/tonybajan/flake8-check-action/check-runs/123',
        data=ANY
    )
    data = json.loads(mock_session.return_value.patch.mock_calls[0].kwargs['data'])
    assert data['status'] == 'completed'
    assert data['output']['summary'] == '*Violations were found*'
    assert len(data['output']['annotations']) == 4


def test_incremental_annotations(monkeypatch):
    monkeypatch.setenv('INPUT_SELECT', 'E,F')

    with patch('flake8_check_action.github.requests.sessions.Session') as mock_session:
        run_check()

    assert mock_session.return_value.patch.call_count == 2


def test_plugins(monkeypatch):
    monkeypatch.setenv('INPUT_SELECT', 'G0, B')

    with patch('flake8_check_action.github.requests.sessions.Session') as mock_session:
        run_check()

    data = json.loads(mock_session.return_value.patch.mock_calls[0].kwargs['data'])
    assert data['status'] == 'completed'
    assert len(data['output']['annotations']) == 1
    assert data['output']['annotations'][0]['title'] == 'B602'
