"""VymoaGaurd PHM mission-assurance prototype."""

from .config import AssessmentConfig
from .contracts import MissionAssessment


def run_assessment(*args, **kwargs):
    """Lazy import wrapper that keeps ``python -m ...replay`` warning-free."""
    from .replay import run_assessment as _run_assessment

    return _run_assessment(*args, **kwargs)

__all__ = ["AssessmentConfig", "MissionAssessment", "run_assessment"]
