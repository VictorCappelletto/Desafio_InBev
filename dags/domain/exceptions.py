"""
Domain Exceptions - Business Rule Violations

Custom exceptions for domain layer.
These represent violations of business rules, not technical errors.
"""

from typing import Dict, Any, Optional


class DomainException(Exception):
    """
    Base exception for domain layer.

    All domain exceptions inherit from this class.
    Represents business rule violations.

    Example:
        >>> raise DomainException("Business rule violated")
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize domain exception.

        Args:
            message: Error message
            details: Additional context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', details={self.details})"


class DomainValidationError(DomainException):
    """
    Validation error in domain layer.

    Raised when a domain object fails validation.

    Example:
        >>> raise DomainValidationError(
        ...     "Brewery name is required",
        ...     details={"field": "name", "value": None}
        ... )
    """

    pass


class InvalidBreweryTypeError(DomainValidationError):
    """
    Invalid brewery type error.

    Raised when brewery type is not in allowed values.

    Example:
        >>> raise InvalidBreweryTypeError(
        ...     "Invalid type: 'invalid'",
        ...     details={"allowed_types": ["micro", "nano", ...]}
        ... )
    """

    pass


class InvalidLocationError(DomainValidationError):
    """
    Invalid location error.

    Raised when location data is invalid.

    Example:
        >>> raise InvalidLocationError(
        ...     "Invalid coordinates",
        ...     details={"latitude": 200, "longitude": -300}
        ... )
    """

    pass


class InvalidContactError(DomainValidationError):
    """
    Invalid contact information error.

    Raised when contact data is invalid.

    Example:
        >>> raise InvalidContactError(
        ...     "Invalid email format",
        ...     details={"email": "not-an-email"}
        ... )
    """

    pass


class EntityNotFoundError(DomainException):
    """
    Entity not found error.

    Raised when requested entity doesn't exist.

    Example:
        >>> raise EntityNotFoundError(
        ...     "Brewery not found",
        ...     details={"id": "abc-123"}
        ... )
    """

    pass


class DuplicateEntityError(DomainException):
    """
    Duplicate entity error.

    Raised when trying to create entity that already exists.

    Example:
        >>> raise DuplicateEntityError(
        ...     "Brewery already exists",
        ...     details={"id": "abc-123", "name": "Existing Brewery"}
        ... )
    """

    pass


class BusinessRuleViolation(DomainException):
    """
    Business rule violation error.

    Raised when a business rule is violated.

    Example:
        >>> raise BusinessRuleViolation(
        ...     "Cannot process closed brewery",
        ...     details={"brewery_id": "abc-123", "status": "closed"}
        ... )
    """

    pass
