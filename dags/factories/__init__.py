"""
Factories Module

Implements Factory Design Pattern for centralized object creation.

Design Patterns:
- Factory Pattern: Encapsulates object creation logic
- Abstract Factory: Returns interfaces, not concrete implementations
- Dependency Injection: Injects configurations into created objects

Benefits:
- Centralized object creation
- Easy to swap implementations
- Testable (can inject mocks)
- Configuration management
- SOLID principles compliance

Usage:
    from factories import ETLFactory

    # Create individual components
    extractor = ETLFactory.create_brewery_extractor()

    # Or create complete pipeline
    extractor, transformer, loader = ETLFactory.create_etl_pipeline()

See Also:
- etl_factory.py: Complete ETL factory implementation
- README.md: Detailed documentation
"""

from .etl_factory import ETLFactory

__all__ = ["ETLFactory"]
