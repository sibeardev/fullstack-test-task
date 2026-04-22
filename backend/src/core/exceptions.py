class EntityNotFoundError(Exception):
    """Raised when a requested domain entity does not exist."""


class ValidationError(Exception):
    """Raised when input violates domain validation rules."""
