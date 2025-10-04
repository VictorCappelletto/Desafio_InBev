"""
Data Transformer Interface

Defines the contract for all data transformation operations.

This interface follows SOLID principles, particularly:
- Dependency Inversion Principle (DIP): High-level code depends on this abstraction
- Liskov Substitution Principle (LSP): All implementations are interchangeable
- Interface Segregation Principle (ISP): Minimal, single-method interface (perfect ISP!)

Design Notes:
- Simple, focused interface with only one method: transform()
- This is a perfect example of ISP: interface does ONE thing well
- Strategy Pattern: Different transformers = different transformation strategies
- Transformers are typically stateless (pure functions on data)

Examples:
    # Cleaning transformer
    class CleaningTransformer(IDataTransformer):
        def transform(self, data):
            return [self._clean_record(r) for r in data]

    # Enrichment transformer
    class EnrichmentTransformer(IDataTransformer):
        def transform(self, data):
            return [self._enrich_record(r) for r in data]

    # Composite transformer (Strategy Pattern)
    def process(data: List[Dict], transformers: List[IDataTransformer]):
        for transformer in transformers:
            data = transformer.transform(data)
        return data
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IDataTransformer(ABC):
    """
    Interface for data transformation operations.

    This interface ensures that all transformers follow the same contract,
    allowing for easy chaining, testing, and swapping of implementations.

    SOLID Principles Applied:
    - Single Responsibility: Only handles data transformation (not extraction/loading)
    - Open/Closed: Open for extension (new transformers), closed for modification
    - Liskov Substitution: All implementations can be used interchangeably
    - Interface Segregation: Perfect ISP - single, focused method
    - Dependency Inversion: High-level modules depend on this abstraction, not concretions

    Strategy Pattern:
    This interface enables the Strategy Pattern, where different transformers
    represent different transformation strategies that can be swapped at runtime.

    Contract:
    - transform(): MUST return transformed data (same structure as input)
    - SHOULD be idempotent (transform(transform(data)) = transform(data))
    - SHOULD handle empty input gracefully

    Thread Safety:
    - Implementations SHOULD be thread-safe (stateless)
    - Avoid mutable state in transformers
    """

    @abstractmethod
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform raw data into cleaned/enriched format.

        This method performs transformations such as:
        - Data cleaning (remove nulls, fix formats)
        - Data enrichment (add calculated fields)
        - Data normalization (standardize formats)
        - Data filtering (remove invalid records)
        - Data aggregation (group/summarize)

        Args:
            data: Raw data to transform. List of dictionaries where each
                 dict represents one record with key-value pairs.

        Returns:
            List[Dict[str, Any]]: Transformed data in the same structure.
                                 Should maintain same or similar schema.
                                 May have fewer records (if filtered).

        Raises:
            TransformationError: If transformation fails
            ValidationError: If input data is invalid

        Example:
            >>> transformer = BreweryTransformer()
            >>> raw_data = [
            ...     {"name": "  Brewery A  ", "city": None},
            ...     {"name": "Brewery B", "city": "NYC"}
            ... ]
            >>> clean_data = transformer.transform(raw_data)
            >>> print(clean_data)
            [
                {"name": "Brewery A", "city": "Unknown"},
                {"name": "Brewery B", "city": "NYC"}
            ]

        Best Practices:
            - Keep transformations pure (no side effects)
            - Log transformation steps for debugging
            - Handle edge cases (empty list, None values)
            - Be idempotent when possible
            - Return empty list if input is empty

        Chaining Transformers:
            >>> data = extractor.extract()
            >>> data = cleaner.transform(data)
            >>> data = enricher.transform(data)
            >>> data = validator.transform(data)
            >>> loader.load(data)
        """
        pass
