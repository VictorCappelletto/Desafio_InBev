"""
Interfaces Module

Defines abstract interfaces following SOLID principles, particularly:
- Dependency Inversion Principle (DIP): Depend on abstractions, not concretions
- Interface Segregation Principle (ISP): Clients shouldn't depend on unused methods
- Liskov Substitution Principle (LSP): Implementations should be interchangeable

These interfaces form the contracts that all service implementations must follow,
enabling polymorphism, testability, and flexibility in the ETL pipeline.

Design Benefits:
- Loose coupling between components
- Easy to swap implementations (e.g., API to Database extractor)
- Testable with mocks
- Type-safe with proper type hints
- Self-documenting through interface contracts

Usage:
    from interfaces import IDataExtractor, IDataLoader, IDataTransformer
    
    # Type hint with interface
    def process_data(extractor: IDataExtractor, loader: IDataLoader):
        data = extractor.extract()
        loader.load(data)

See Also:
- services/: Concrete implementations of these interfaces
- factories/: Factory methods for creating instances
- README.md: Detailed documentation
"""

from .data_extractor import IDataExtractor
from .data_loader import IDataLoader
from .data_transformer import IDataTransformer

__all__ = [
    "IDataExtractor",
    "IDataLoader",
    "IDataTransformer",
]

