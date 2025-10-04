"""
Value Objects - Immutable Domain Objects

Value objects represent descriptive aspects of the domain with no identity.
They are immutable and equality is based on their attributes.

DDD Principles:
- Immutability: Cannot be modified after creation
- Value Equality: Two objects with same values are equal
- Self-Validation: Validates on construction
- Side-Effect Free: Operations return new instances

Examples:
- Money(amount=100, currency="USD")
- DateRange(start=date1, end=date2)
- Location(city="Portland", state="Oregon")
"""

from dataclasses import dataclass
from typing import Optional
import re


@dataclass(frozen=True)
class Coordinates:
    """
    Geographic coordinates value object.

    Represents a point on Earth with latitude and longitude.
    Immutable and self-validating.

    Attributes:
        latitude: Latitude (-90 to 90)
        longitude: Longitude (-180 to 180)

    Example:
        >>> coords = Coordinates(latitude=45.5152, longitude=-122.6784)
        >>> coords.is_valid()
        True
        >>> coords.to_dict()
        {'latitude': 45.5152, 'longitude': -122.6784}

    Raises:
        ValueError: If coordinates are out of valid range
    """

    latitude: float
    longitude: float

    def __post_init__(self):
        """Validate coordinates after initialization."""
        if not (-90 <= self.latitude <= 90):
            raise ValueError(
                f"Latitude must be between -90 and 90, got {self.latitude}"
            )
        if not (-180 <= self.longitude <= 180):
            raise ValueError(
                f"Longitude must be between -180 and 180, got {self.longitude}"
            )

    def is_valid(self) -> bool:
        """Check if coordinates are valid."""
        return -90 <= self.latitude <= 90 and -180 <= self.longitude <= 180

    def to_dict(self):
        """Convert to dictionary."""
        return {"latitude": self.latitude, "longitude": self.longitude}

    def __str__(self) -> str:
        return f"{self.latitude:.4f}, {self.longitude:.4f}"


@dataclass(frozen=True)
class Address:
    """
    Physical address value object.

    Represents a complete mailing address.
    Immutable and self-validating.

    Attributes:
        street: Street address (optional)
        city: City name
        state: State/Province
        country: Country name
        postal_code: Postal/ZIP code (optional)

    Example:
        >>> address = Address(
        ...     street="123 Main St",
        ...     city="Portland",
        ...     state="Oregon",
        ...     country="United States",
        ...     postal_code="97201"
        ... )
        >>> address.is_complete()
        True
        >>> str(address)
        '123 Main St, Portland, Oregon 97201, United States'
    """

    city: str
    state: str
    country: str
    street: Optional[str] = None
    postal_code: Optional[str] = None

    def __post_init__(self):
        """Validate address after initialization."""
        if not self.city or not self.city.strip():
            raise ValueError("City is required")
        if not self.state or not self.state.strip():
            raise ValueError("State is required")
        if not self.country or not self.country.strip():
            raise ValueError("Country is required")

    def is_complete(self) -> bool:
        """Check if address has all components."""
        return bool(
            self.street
            and self.city
            and self.state
            and self.country
            and self.postal_code
        )

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "postal_code": self.postal_code,
        }

    def __str__(self) -> str:
        """Format address as string."""
        parts = []
        if self.street:
            parts.append(self.street)
        parts.append(self.city)

        state_zip = self.state
        if self.postal_code:
            state_zip += f" {self.postal_code}"
        parts.append(state_zip)

        parts.append(self.country)

        return ", ".join(parts)


@dataclass(frozen=True)
class Location:
    """
    Complete location value object.

    Combines address and coordinates for a physical location.
    Immutable aggregate of Address and Coordinates.

    Attributes:
        address: Physical address
        coordinates: Geographic coordinates (optional)

    Example:
        >>> address = Address(city="Portland", state="Oregon", country="USA")
        >>> coords = Coordinates(latitude=45.5152, longitude=-122.6784)
        >>> location = Location(address=address, coordinates=coords)
        >>> location.has_coordinates()
        True
        >>> location.is_in_usa()
        True
    """

    address: Address
    coordinates: Optional[Coordinates] = None

    def has_coordinates(self) -> bool:
        """Check if location has valid coordinates."""
        return self.coordinates is not None and self.coordinates.is_valid()

    def is_in_usa(self) -> bool:
        """Check if location is in United States."""
        return self.address.country.lower() in [
            "united states",
            "usa",
            "us",
            "united states of america",
        ]

    def is_complete(self) -> bool:
        """Check if location has complete information."""
        return self.address.is_complete() and self.has_coordinates()

    def to_dict(self):
        """Convert to dictionary."""
        data = {
            "address": self.address.to_dict(),
        }
        if self.coordinates:
            data["coordinates"] = self.coordinates.to_dict()
        return data

    def __str__(self) -> str:
        """Format location as string."""
        result = str(self.address)
        if self.coordinates:
            result += f" ({self.coordinates})"
        return result


@dataclass(frozen=True)
class Contact:
    """
    Contact information value object.

    Represents various ways to contact a business.
    Immutable and self-validating.

    Attributes:
        phone: Phone number (optional)
        website_url: Website URL (optional)
        email: Email address (optional)

    Example:
        >>> contact = Contact(
        ...     phone="503-555-0123",
        ...     website_url="https://brewery.com",
        ...     email="info@brewery.com"
        ... )
        >>> contact.has_any()
        True
        >>> contact.is_email_valid()
        True

    Raises:
        ValueError: If email or URL format is invalid
    """

    phone: Optional[str] = None
    website_url: Optional[str] = None
    email: Optional[str] = None

    def __post_init__(self):
        """Validate contact information after initialization."""
        if self.email and not self._is_email_valid(self.email):
            raise ValueError(f"Invalid email format: {self.email}")

        if self.website_url and not self._is_url_valid(self.website_url):
            raise ValueError(f"Invalid URL format: {self.website_url}")

    @staticmethod
    def _is_email_valid(email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def _is_url_valid(url: str) -> bool:
        """Validate URL format."""
        pattern = r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*$"
        return bool(re.match(pattern, url))

    def has_any(self) -> bool:
        """Check if any contact method is provided."""
        return bool(self.phone or self.website_url or self.email)

    def has_all(self) -> bool:
        """Check if all contact methods are provided."""
        return bool(self.phone and self.website_url and self.email)

    def is_email_valid(self) -> bool:
        """Check if email is valid."""
        return bool(self.email and self._is_email_valid(self.email))

    def is_url_valid(self) -> bool:
        """Check if URL is valid."""
        return bool(self.website_url and self._is_url_valid(self.website_url))

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "phone": self.phone,
            "website_url": self.website_url,
            "email": self.email,
        }

    def __str__(self) -> str:
        """Format contact as string."""
        parts = []
        if self.phone:
            parts.append(f"📞 {self.phone}")
        if self.website_url:
            parts.append(f"🌐 {self.website_url}")
        if self.email:
            parts.append(f"📧 {self.email}")
        return " | ".join(parts) if parts else "No contact info"


@dataclass(frozen=True)
class BreweryType:
    """
    Brewery type value object.

    Represents the type/category of a brewery with validation.

    Valid Types:
        - micro: Small craft brewery
        - nano: Very small brewery
        - regional: Regional brewery
        - brewpub: Brewery with pub
        - large: Large commercial brewery
        - planning: In planning phase
        - contract: Contract brewer
        - proprietor: Proprietor brewery
        - closed: No longer operating

    Example:
        >>> brewery_type = BreweryType("micro")
        >>> brewery_type.is_active()
        True
        >>> brewery_type.is_craft()
        True

    Raises:
        ValueError: If brewery type is invalid
    """

    value: str

    VALID_TYPES = {
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

    CRAFT_TYPES = {"micro", "nano", "brewpub"}
    ACTIVE_TYPES = {
        "micro",
        "nano",
        "regional",
        "brewpub",
        "large",
        "contract",
        "proprietor",
    }

    def __post_init__(self):
        """Validate brewery type after initialization."""
        if self.value.lower() not in self.VALID_TYPES:
            raise ValueError(
                f"Invalid brewery type: {self.value}. "
                f"Must be one of: {', '.join(sorted(self.VALID_TYPES))}"
            )

    def is_active(self) -> bool:
        """Check if brewery type indicates active operation."""
        return self.value.lower() in self.ACTIVE_TYPES

    def is_craft(self) -> bool:
        """Check if brewery is craft brewery."""
        return self.value.lower() in self.CRAFT_TYPES

    def is_closed(self) -> bool:
        """Check if brewery is closed."""
        return self.value.lower() == "closed"

    def is_planning(self) -> bool:
        """Check if brewery is in planning phase."""
        return self.value.lower() == "planning"

    def __str__(self) -> str:
        return self.value.lower()
