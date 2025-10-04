"""
Domain Validators - Business Rule Validation

Validators encapsulate complex business rules.
They are stateless and side-effect free.
"""

from typing import Any, Dict, List, Tuple

from .entities import Brewery, BreweryAggregate
from .value_objects import BreweryType, Contact, Location


class BreweryValidator:
    """
    Validates brewery business rules.

    Stateless validator for complex brewery validation logic.

    Example:
        >>> validator = BreweryValidator()
        >>> is_valid, errors = validator.validate_for_processing(brewery)
        >>> if not is_valid:
        ...     print(f"Errors: {errors}")
    """

    @staticmethod
    def validate_for_processing(brewery: Brewery) -> Tuple[bool, List[str]]:
        """
        Validate if brewery can be processed.

        Args:
            brewery: Brewery to validate

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        # Required fields
        if not brewery.id:
            errors.append("Brewery ID is required")

        if not brewery.name or len(brewery.name.strip()) < 2:
            errors.append("Brewery name must be at least 2 characters")

        # Business rules
        if not brewery.is_active():
            errors.append("Only active breweries can be processed")

        if not brewery.has_location():
            errors.append("Location is required for processing")

        return len(errors) == 0, errors

    @staticmethod
    def validate_for_export(brewery: Brewery) -> Tuple[bool, List[str]]:
        """
        Validate if brewery can be exported.

        Args:
            brewery: Brewery to validate

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        # All required fields for export
        if not brewery.id:
            errors.append("ID required")

        if not brewery.name:
            errors.append("Name required")

        if not brewery.has_location():
            errors.append("Location required")

        if not brewery.location or not brewery.location.address:
            errors.append("Address required")

        return len(errors) == 0, errors

    @staticmethod
    def validate_completeness(brewery: Brewery) -> Dict[str, Any]:
        """
        Check data completeness.

        Args:
            brewery: Brewery to check

        Returns:
            Dictionary with completeness metrics
        """
        checks = {
            "has_id": bool(brewery.id),
            "has_name": bool(brewery.name),
            "has_type": bool(brewery.brewery_type),
            "has_location": brewery.has_location(),
            "has_address": bool(brewery.location and brewery.location.address),
            "has_coordinates": brewery.has_coordinates(),
            "has_contact": brewery.has_contact(),
            "has_phone": bool(brewery.contact and brewery.contact.phone),
            "has_website": bool(brewery.contact and brewery.contact.website_url),
            "has_email": bool(brewery.contact and brewery.contact.email),
        }

        total_checks = len(checks)
        passed_checks = sum(1 for v in checks.values() if v)

        return {
            "checks": checks,
            "completeness_score": passed_checks / total_checks,
            "passed": passed_checks,
            "total": total_checks,
            "missing": [k for k, v in checks.items() if not v],
        }

    @staticmethod
    def calculate_quality_score(brewery: Brewery) -> float:
        """
        Calculate overall quality score.

        Args:
            brewery: Brewery to score

        Returns:
            Quality score (0.0 to 1.0)
        """
        aggregate = BreweryAggregate(brewery)
        return aggregate.get_quality_score()


class LocationValidator:
    """Validates location business rules."""

    @staticmethod
    def is_valid_for_mapping(location: Location) -> bool:
        """
        Check if location can be mapped.

        Args:
            location: Location to validate

        Returns:
            True if has valid coordinates
        """
        return location.has_coordinates()

    @staticmethod
    def is_complete(location: Location) -> bool:
        """
        Check if location has all required fields.

        Args:
            location: Location to check

        Returns:
            True if complete
        """
        return location.is_complete()


class ContactValidator:
    """Validates contact business rules."""

    @staticmethod
    def has_valid_contact_method(contact: Contact) -> bool:
        """
        Check if at least one contact method is valid.

        Args:
            contact: Contact to validate

        Returns:
            True if has valid contact
        """
        return contact.has_any()

    @staticmethod
    def validate_all_methods(contact: Contact) -> Dict[str, bool]:
        """
        Validate all contact methods.

        Args:
            contact: Contact to validate

        Returns:
            Dictionary with validation results
        """
        return {
            "phone": bool(contact.phone),
            "email": contact.is_email_valid(),
            "website": contact.is_url_valid(),
            "has_any": contact.has_any(),
            "has_all": contact.has_all(),
        }
