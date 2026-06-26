class OmniBrowseError(Exception):
    """Base application exception."""


class ControlModeUnavailable(OmniBrowseError):
    """Raised when no browser control mode can handle a task."""


class SafetyBlocked(OmniBrowseError):
    """Raised when the policy checker blocks an action."""

