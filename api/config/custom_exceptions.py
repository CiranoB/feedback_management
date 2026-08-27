class DuplicateNotationError(Exception):
    """Raised when a user attempts to add multiple notation to a target."""


class FeedbackNotFoundError(Exception):
    """Raised when attempting to update the status of a feedback that does not exist."""
