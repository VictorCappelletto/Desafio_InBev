"""
Domain Entities - Core Business Objects

Entities have identity and lifecycle.
Unlike value objects, entities are mutable and equality is based on ID.

DDD Principles:
- Identity: Unique identifier
- Mutable: Can change over time
- Lifecycle: Create, update, delete
- Business Logic: Encapsulates rules
- Consistency: Validates state
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .exceptions import DomainValidationError
from .value_objects import Address, BreweryType, Contact, Coordinates, Location


@dataclass
class Brewery:
    """
    Brewery entity - Core domain object.

    Represents a brewery with identity, location, and contact information.
    Encapsulates business rules and validation logic.

    Attributes:
        id: Unique identifier (required)
        name: Brewery name (required)
        brewery_type: Type of brewery (required)
        location: Physical location (optional)
        contact: Contact information (optional)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        metadata: Additional data

    Example:
        >>> brewery = Brewery(
        ...     id="abc-123",
        ...     name="Great Brewery",
        ...     brewery_type=BreweryType("micro"),
        ...     location=Location(...),
        ...     contact=Contact(...)
        ... )
        >>> brewery.validate()
        >>> brewery.is_active()
        True
    """

    # Required fields
    id: str
    name: str
    brewery_type: BreweryType

    # Optional fields
    location: Optional[Location] = None
    contact: Optional[Contact] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate entity after initialization."""
        self.validate()

    def validate(self) -> None:
        """
        Validate entity state.

        Raises:
            DomainValidationError: If validation fails
        """
        errors = []

        # ID validation
        if not self.id or not str(self.id).strip():
            errors.append("ID is required")

        # Name validation
        if not self.name or not self.name.strip():
            errors.append("Name is required")
        elif len(self.name) < 2:
            errors.append("Name must be at least 2 characters")
        elif len(self.name) > 200:
            errors.append("Name must be less than 200 characters")

        # Type validation
        if not self.brewery_type:
            errors.append("Brewery type is required")

        if errors:
            raise DomainValidationError(
                f"Brewery validation failed: {', '.join(errors)}",
                details={"errors": errors, "id": self.id, "name": self.name},
            )

    def is_active(self) -> bool:
        """
        Check if brewery is active.

        Returns:
            True if brewery is active (not closed or planning)
        """
        return self.brewery_type.is_active()

    def is_craft(self) -> bool:
        """
        Check if brewery is craft brewery.

        Returns:
            True if brewery is craft (micro, nano, brewpub)
        """
        return self.brewery_type.is_craft()

    def is_complete(self) -> bool:
        """
        Check if brewery has complete information.

        Returns:
            True if has location and contact info
        """
        return (
            self.location is not None
            and self.location.is_complete()
            and self.contact is not None
            and self.contact.has_any()
        )

    def has_location(self) -> bool:
        """Check if brewery has location information."""
        return self.location is not None

    def has_contact(self) -> bool:
        """Check if brewery has contact information."""
        return self.contact is not None and self.contact.has_any()

    def has_coordinates(self) -> bool:
        """Check if brewery has geographic coordinates."""
        return self.location is not None and self.location.has_coordinates()

    def update(
        self,
        name: Optional[str] = None,
        brewery_type: Optional[BreweryType] = None,
        location: Optional[Location] = None,
        contact: Optional[Contact] = None,
        **metadata,
    ) -> "Brewery":
        """
        Update brewery information.

        Returns new instance (entities are immutable).

        Args:
            name: New name
            brewery_type: New type
            location: New location
            contact: New contact
            **metadata: Additional metadata

        Returns:
            New Brewery instance with updates
        """
        return Brewery(
            id=self.id,
            name=name or self.name,
            brewery_type=brewery_type or self.brewery_type,
            location=location or self.location,
            contact=contact or self.contact,
            created_at=self.created_at,
            updated_at=datetime.now(),
            metadata={**self.metadata, **metadata},
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dictionary representation
        """
        data = {
            "id": self.id,
            "name": self.name,
            "brewery_type": str(self.brewery_type),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active(),
            "is_craft": self.is_craft(),
            "is_complete": self.is_complete(),
        }

        if self.location:
            data["location"] = self.location.to_dict()

        if self.contact:
            data["contact"] = self.contact.to_dict()

        if self.metadata:
            data["metadata"] = self.metadata

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Brewery":
        """
        Create Brewery from dictionary.

        Args:
            data: Dictionary with brewery data

        Returns:
            New Brewery instance

        Example:
            >>> data = {
            ...     "id": "abc-123",
            ...     "name": "Great Brewery",
            ...     "brewery_type": "micro",
            ...     "city": "Portland",
            ...     "state": "Oregon",
            ...     "country": "United States"
            ... }
            >>> brewery = Brewery.from_dict(data)
        """
        # Extract brewery type
        brewery_type = BreweryType(data.get("brewery_type", "micro"))

        # Extract location if available
        location = None
        if any(key in data for key in ["city", "state", "country"]):
            address = Address(
                street=data.get("address_1") or data.get("street"),
                city=data.get("city", ""),
                state=data.get("state", ""),
                country=data.get("country", ""),
                postal_code=data.get("postal_code"),
            )

            coordinates = None
            if "latitude" in data and "longitude" in data:
                try:
                    lat = float(data["latitude"])
                    lon = float(data["longitude"])
                    coordinates = Coordinates(latitude=lat, longitude=lon)
                except (ValueError, TypeError):
                    pass

            location = Location(address=address, coordinates=coordinates)

        # Extract contact if available
        contact = None
        if any(key in data for key in ["phone", "website_url", "email"]):
            try:
                contact = Contact(
                    phone=data.get("phone"),
                    website_url=data.get("website_url"),
                    email=data.get("email"),
                )
            except ValueError:
                # Invalid contact data, skip
                pass

        # Extract timestamps
        created_at = datetime.now()
        updated_at = datetime.now()

        if "created_at" in data:
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                pass

        if "updated_at" in data:
            try:
                updated_at = datetime.fromisoformat(data["updated_at"])
            except (ValueError, TypeError):
                pass

        return cls(
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            brewery_type=brewery_type,
            location=location,
            contact=contact,
            created_at=created_at,
            updated_at=updated_at,
            metadata=data.get("metadata", {}),
        )

    def __eq__(self, other) -> bool:
        """Equality based on ID."""
        if not isinstance(other, Brewery):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    def __str__(self) -> str:
        """String representation."""
        return (
            f"Brewery(id='{self.id}', name='{self.name}', type='{self.brewery_type}')"
        )

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"Brewery(id='{self.id}', name='{self.name}', "
            f"type='{self.brewery_type}', active={self.is_active()})"
        )


@dataclass
class BreweryAggregate:
    """
    Brewery aggregate root.

    Manages consistency of brewery and its related entities.
    Acts as entry point for all operations on the brewery.

    DDD Aggregate Pattern:
    - Root entity: Brewery
    - Value objects: Location, Contact
    - Invariants: Business rules
    - Transactional boundary

    Example:
        >>> aggregate = BreweryAggregate(brewery)
        >>> aggregate.validate_consistency()
        >>> aggregate.can_be_processed()
        True
    """

    brewery: Brewery
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def validate_consistency(self) -> bool:
        """
        Validate aggregate consistency.

        Checks all business rules and invariants.

        Returns:
            True if consistent, False otherwise
        """
        self.validation_errors.clear()
        self.warnings.clear()

        try:
            self.brewery.validate()
        except DomainValidationError as e:
            self.validation_errors.append(str(e))
            return False

        # Business rules validation
        if not self.brewery.has_location():
            self.warnings.append("Brewery has no location information")

        if not self.brewery.has_contact():
            self.warnings.append("Brewery has no contact information")

        if not self.brewery.has_coordinates():
            self.warnings.append("Brewery has no geographic coordinates")

        if self.brewery.brewery_type.is_closed():
            self.warnings.append("Brewery is marked as closed")

        return len(self.validation_errors) == 0

    def can_be_processed(self) -> bool:
        """
        Check if brewery can be processed.

        Returns:
            True if brewery meets processing requirements
        """
        return (
            self.validate_consistency()
            and self.brewery.is_active()
            and self.brewery.has_location()
        )

    def get_quality_score(self) -> float:
        """
        Calculate data quality score.

        Returns:
            Quality score (0.0 to 1.0)
        """
        score = 0.0
        total_checks = 6

        # Required fields (base score)
        if self.brewery.id and self.brewery.name:
            score += 0.3

        # Location
        if self.brewery.has_location():
            score += 0.2

        # Coordinates
        if self.brewery.has_coordinates():
            score += 0.2

        # Contact
        if self.brewery.has_contact():
            score += 0.15

        # Complete location
        if self.brewery.location and self.brewery.location.is_complete():
            score += 0.1

        # Active status
        if self.brewery.is_active():
            score += 0.05

        return min(score, 1.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert aggregate to dictionary."""
        return {
            "brewery": self.brewery.to_dict(),
            "validation_errors": self.validation_errors,
            "warnings": self.warnings,
            "can_be_processed": self.can_be_processed(),
            "quality_score": self.get_quality_score(),
        }

    def __str__(self) -> str:
        return f"BreweryAggregate({self.brewery})"
