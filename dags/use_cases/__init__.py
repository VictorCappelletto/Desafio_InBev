"""
Use Cases Layer - Application Logic

Contains application-specific business rules (use cases).
This layer orchestrates domain entities and external services.

Clean Architecture:
    External        → Services (HTTP, DB, Files)
    Adapters        → Repositories (data access)
    Use Cases       → Application logic (THIS LAYER)
    Domain          → Business rules

SOLID Principles:
- Single Responsibility: Each use case does one thing
- Open/Closed: Easy to add new use cases
- Liskov Substitution: Use cases are substitutable
- Interface Segregation: Focused interfaces
- Dependency Inversion: Depends on interfaces, not implementations

Use Case Pattern:
- Input: Request DTO
- Process: Domain logic + repository calls
- Output: Response DTO
- Error Handling: Domain exceptions → use case exceptions

Benefits:
- Clear application boundaries
- Testable without infrastructure
- Reusable across interfaces (Web, CLI, API)
- Domain logic protected
- Independent of frameworks

Usage Example:
    from use_cases import ExtractBreweriesUseCase, TransformBreweriesUseCase
    from repositories import BreweryRepository

    # Extract
    extract_uc = ExtractBreweriesUseCase(api_extractor)
    breweries_data = extract_uc.execute()

    # Transform
    transform_uc = TransformBreweriesUseCase()
    breweries = transform_uc.execute(breweries_data)

    # Load
    load_uc = LoadBreweriesUseCase(repository)
    loaded_count = load_uc.execute(breweries)

See Also:
- use_cases/extract.py: Data extraction use cases
- use_cases/transform.py: Data transformation use cases
- use_cases/load.py: Data loading use cases
- use_cases/quality.py: Data quality use cases
"""

from .extract import ExtractBreweriesUseCase
from .load import LoadBreweriesUseCase
from .quality import ValidateBreweriesQualityUseCase
from .transform import TransformBreweriesUseCase

__all__ = [
    "ExtractBreweriesUseCase",
    "TransformBreweriesUseCase",
    "LoadBreweriesUseCase",
    "ValidateBreweriesQualityUseCase",
]
