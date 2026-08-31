class DuplicateNotationError(Exception):
    """Raised when a user attempts to add multiple notation to a target."""


class FeedbackNotFoundError(Exception):
    """Raised when attempting to operate on a feedback that does not exist."""


class FeedbackMergeError(Exception):
    """Raised when a feedback merge request is invalid."""
