from typing import Optional

from flake8.formatting.default import Default
from flake8.style_guide import Violation


class GitHubCheckFormatter(Default):
    def after_init(self) -> None:
        self.check_run = None
        self.violations_seen = False
        self.violations_outstanding = []

    def format(self, error: Violation) -> Optional[str]:
        self.violations_seen = True
        self.violations_outstanding.append(error)
        if len(self.violations_outstanding) == 50:
            self.check_run.send_outstanding_annotations(self)
            self.violations_outstanding = []
        return super().format(error)
