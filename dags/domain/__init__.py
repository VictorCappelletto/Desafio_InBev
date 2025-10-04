"""
Domain Layer - Clean Architecture

Core business entities and value objects with business rules.
This layer is independent of external frameworks and infrastructure.

Clean Architecture Layers:
    External        → Infrastructure (DB, APIs, Files)
    Adapters        → Services (implementations)
    Use Cases       → Application logic
    Domain          → Business rules (THIS LAYER)

SOLID Principles:
- Single Responsibility: Each entity manages one business concept
- Open/Closed: Extend via inheritance, closed for modification
- Liskov Substitution: Value objects are immutable and substitutable
- Interface Segregation: Focused interfaces
- Dependency Inversion: Domain has zero external dependencies

Domain-Driven Design (DDD):
- Entities: Objects with identity (e.g., Brewery with ID)
- Value Objects: Immutable objects without identity (e.g., Location)
- Aggregates: Clusters of entities (e.g., Brewery + Location)
- Domain Events: Business events that occur

Benefits:
- Zero external dependencies (most testable layer)
- Business rules centralized
- Type safety with value objects
- Immutability prevents bugs
- Clear domain model

Usage Example:
    from domain import Brewery, Location, Contact
    
    # Create value objects
    location = Location(
        address="123 Main St",
        city="Portland",
        state="Oregon",
        country="United States",
        postal_code="97201",
        latitude=45.5152,
        longitude=-122.6784
    )
    
    contact = Contact(
        phone="503-555-0123",
        website_url="https://brewery.com",
        email="info@brewery.com"
    )
    
    # Create entity
    brewery = Brewery(
        id="abc-123",
        name="Great Brewery",
        brewery_type="micro",
        location=location,
        contact=contact
    )
    
    # Business rules enforced
    print(brewery.is_active())  # True if has recent activity
    print(brewery.validate())   # Validation result

See Also:
- domain/entities.py: Core business entities
- domain/value_objects.py: Immutable value objects
- domain/exceptions.py: Domain-specific exceptions
- domain/validators.py: Business rule validators
"""

from .entities import Brewery, BreweryAggregate
from .value_objects import Location, Contact, Coordinates, Address
from .exceptions import DomainValidationError, InvalidBreweryTypeError
from .validators import BreweryValidator

__all__ = [
    # Entities
    "Brewery",
    "BreweryAggregate",
    # Value Objects
    "Location",
    "Contact",
    "Coordinates",
    "Address",
    # Exceptions
    "DomainValidationError",
    "InvalidBreweryTypeError",
    # Validators
    "BreweryValidator",
]

