"""
Brewery-Specific Data Quality Rules

Business-specific validation rules for brewery data based on domain knowledge.
"""

from typing import Dict, Any, List
from ..framework import DataQualityEngine
from ..dimensions import (
    CompletenessCheck,
    AccuracyCheck,
    ConsistencyCheck,
    ValidityCheck,
    UniquenessCheck,
)


# Valid brewery types based on Open Brewery DB schema
VALID_BREWERY_TYPES = {
    "micro",
    "nano",
    "regional",
    "brewpub",
    "large",
    "planning",
    "contract",
    "proprietor",
    "closed",
}

# US States (for validation)
VALID_US_STATES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
}


def create_brewery_quality_engine(strict_mode: bool = False) -> DataQualityEngine:
    """
    Create a preconfigured data quality engine for brewery data.

    Args:
        strict_mode: If True, use stricter thresholds (default: False)

    Returns:
        DataQualityEngine configured with brewery-specific checks

    Example:
        >>> engine = create_brewery_quality_engine(strict_mode=True)
        >>> report = engine.run_checks(brewery_data)
        >>> if not report.passed:
        ...     raise DataQualityException("Quality checks failed")
    """
    threshold = 0.99 if strict_mode else 0.95

    engine = DataQualityEngine(min_overall_score=threshold)

    # 1. Completeness: Critical fields must be present
    engine.add_check(
        CompletenessCheck(
            required_fields=["id", "name", "brewery_type"],
            threshold=1.0,  # Strict: all critical fields required
            weight=2.0,  # High importance
        )
    )

    # 2. Completeness: Important location fields
    engine.add_check(
        CompletenessCheck(
            required_fields=["city", "state", "country"],
            threshold=0.90,  # 90% should have location
            weight=1.5,
        )
    )

    # 3. Accuracy: Validate brewery type
    engine.add_check(
        AccuracyCheck(
            field_validators={
                "brewery_type": lambda x: x in VALID_BREWERY_TYPES if x else False,
            },
            threshold=1.0,  # All brewery types must be valid
            weight=2.0,
        )
    )

    # 4. Accuracy: Validate state codes
    engine.add_check(
        AccuracyCheck(
            field_validators={
                "state": lambda x: (
                    x in VALID_US_STATES if x else True
                ),  # Optional but must be valid
            },
            threshold=0.95,
            weight=1.0,
        )
    )

    # 5. Accuracy: Validate coordinates (if present)
    engine.add_check(
        AccuracyCheck(
            field_validators={
                "latitude": lambda x: -90 <= float(x) <= 90 if x else True,
                "longitude": lambda x: -180 <= float(x) <= 180 if x else True,
            },
            threshold=0.95,
            weight=1.0,
        )
    )

    # 6. Consistency: Business rules
    business_rules = [
        # If city is present, state should be present too
        lambda r: r.get("state") is not None if r.get("city") else True,
        # If coordinates present, both lat and lon must be present
        lambda r: (r.get("latitude") and r.get("longitude"))
        or (not r.get("latitude") and not r.get("longitude")),
        # Name should have reasonable length
        lambda r: 2 <= len(r.get("name", "")) <= 200,
        # Closed breweries should not have recent updates (if timestamp available)
        lambda r: r.get("brewery_type") != "closed" or not r.get("is_recent", True),
    ]

    engine.add_check(
        ConsistencyCheck(
            business_rules=business_rules,
            rule_names=[
                "city_implies_state",
                "coordinates_complete",
                "name_length_valid",
                "closed_brewery_inactive",
            ],
            threshold=0.95,
            weight=1.5,
        )
    )

    # 7. Validity: Schema validation
    schema = {
        "id": str,
        "name": str,
        "brewery_type": str,
        "address_1": (str, type(None)),
        "address_2": (str, type(None)),
        "address_3": (str, type(None)),
        "city": (str, type(None)),
        "state_province": (str, type(None)),
        "postal_code": (str, type(None)),
        "country": (str, type(None)),
        "longitude": (str, float, type(None)),
        "latitude": (str, float, type(None)),
        "phone": (str, type(None)),
        "website_url": (str, type(None)),
        "state": (str, type(None)),
        "street": (str, type(None)),
    }

    engine.add_check(ValidityCheck(schema=schema, threshold=0.95, weight=1.0))

    # 8. Uniqueness: IDs must be unique
    engine.add_check(
        UniquenessCheck(
            key_fields="id",
            threshold=1.0,  # No duplicates allowed
            weight=2.0,  # Critical
        )
    )

    return engine


def validate_brewery_name(name: str) -> bool:
    """
    Validate brewery name.

    Args:
        name: Brewery name to validate

    Returns:
        True if name is valid, False otherwise

    Rules:
        - Not empty
        - Between 2 and 200 characters
        - No suspicious patterns
    """
    if not name or not isinstance(name, str):
        return False

    name = name.strip()

    if len(name) < 2 or len(name) > 200:
        return False

    # Check for suspicious patterns
    suspicious_patterns = ["test", "xxx", "null", "undefined"]
    name_lower = name.lower()
    if any(pattern in name_lower for pattern in suspicious_patterns):
        return False

    return True


def validate_coordinates(latitude: Any, longitude: Any) -> bool:
    """
    Validate geographic coordinates.

    Args:
        latitude: Latitude value
        longitude: Longitude value

    Returns:
        True if coordinates are valid, False otherwise
    """
    try:
        if latitude is None and longitude is None:
            return True  # Both null is acceptable

        if latitude is None or longitude is None:
            return False  # One null, one filled is invalid

        lat = float(latitude)
        lon = float(longitude)

        # Valid ranges
        if not (-90 <= lat <= 90):
            return False
        if not (-180 <= lon <= 180):
            return False

        # Check for obvious invalid values (0,0 is suspicious)
        if lat == 0 and lon == 0:
            return False

        return True

    except (ValueError, TypeError):
        return False


def get_critical_field_validators() -> Dict[str, Any]:
    """
    Get validators for critical brewery fields.

    Returns:
        Dict mapping field names to validator functions

    Example:
        >>> validators = get_critical_field_validators()
        >>> check = AccuracyCheck(validators)
        >>> result = check.check(data)
    """
    return {
        "id": lambda x: isinstance(x, str) and len(x) > 0,
        "name": validate_brewery_name,
        "brewery_type": lambda x: x in VALID_BREWERY_TYPES,
        "country": lambda x: isinstance(x, str) and len(x) > 0 if x else True,
    }


def get_location_field_validators() -> Dict[str, Any]:
    """
    Get validators for location fields.

    Returns:
        Dict mapping field names to validator functions
    """
    return {
        "state": lambda x: x in VALID_US_STATES if x else True,
        "postal_code": lambda x: len(str(x)) in [5, 10] if x else True,  # US zip codes
        "city": lambda x: 2 <= len(str(x)) <= 100 if x else True,
    }


# Example: Custom quality check for specific business need
class BreweryContactCheck(AccuracyCheck):
    """
    Custom check: Breweries should have at least one contact method.

    Example:
        >>> check = BreweryContactCheck()
        >>> result = check.check(brewery_data)
    """

    def __init__(self, threshold: float = 0.80, weight: float = 1.0):
        """
        Initialize contact check.

        Args:
            threshold: Minimum % of breweries with contact info (default: 0.80)
            weight: Importance weight (default: 1.0)
        """
        validators = {
            "_has_contact": lambda r: (
                r.get("phone") or r.get("website_url") or r.get("email")
            )
        }

        super().__init__(
            field_validators=validators, threshold=threshold, weight=weight
        )
