"""
Repository Layer - Data Access Abstraction

Repositories abstract data access, providing a collection-like interface
for domain entities. This layer adapts between domain and infrastructure.

Clean Architecture:
    External        → Database, Files, APIs
    Adapters        → Repositories (THIS LAYER)
    Use Cases       → Application logic
    Domain          → Business rules

Repository Pattern Benefits:
- Domain doesn't know about database
- Easily swap implementations (SQL → NoSQL)
- Testable with in-memory repositories
- Clear separation of concerns
- Query logic centralized

SOLID Principles:
- Single Responsibility: Only handles data access
- Open/Closed: Add new repositories without changing existing
- Liskov Substitution: All repositories implement IRepository
- Interface Segregation: Focused repository interfaces
- Dependency Inversion: Use cases depend on IRepository, not concrete DB

Usage Example:
    from repositories import BreweryRepository, InMemoryBreweryRepository
    from domain import Brewery

    # Production: SQL database
    repo = BreweryRepository(connection)

    # Testing: In-memory
    repo = InMemoryBreweryRepository()

    # Use same interface
    brewery = repo.get_by_id("abc-123")
    repo.add(brewery)
    repo.save()

See Also:
- repositories/base.py: Base repository interfaces
- repositories/brewery_repository.py: Brewery repository implementations
- repositories/unit_of_work.py: Transaction management
"""

from .base import IBreweryRepository, IRepository
from .brewery_repository import (
    InMemoryBreweryRepository,
    SQLBreweryRepository,
)
from .unit_of_work import InMemoryUnitOfWork, UnitOfWork

__all__ = [
    # Interfaces
    "IRepository",
    "IBreweryRepository",
    # Implementations
    "InMemoryBreweryRepository",
    "SQLBreweryRepository",
    # Unit of Work
    "UnitOfWork",
    "InMemoryUnitOfWork",
]
