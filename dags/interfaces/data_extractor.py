"""
Data Extractor Interface

Defines the contract for all data extraction operations.

This interface follows SOLID principles, particularly:
- Dependency Inversion Principle (DIP): High-level code depends on this abstraction
- Liskov Substitution Principle (LSP): All implementations are interchangeable
- Interface Segregation Principle (ISP): Minimal, focused interface

Design Notes:
- Keep methods minimal (currently: extract, validate_data)
- Validation is optional but recommended for data quality
- If an extractor doesn't need validation, can return True by default
- Future: Consider splitting validation into separate interface if needed

Examples:
    # Implementing the interface
    class MyExtractor(IDataExtractor):
        def extract(self) -> List[Dict[str, Any]]:
            return [{"id": 1, "name": "Test"}]

        def validate_data(self, data: List[Dict[str, Any]]) -> bool:
            return len(data) > 0

    # Using the interface
    def process(extractor: IDataExtractor):
        data = extractor.extract()
        if extractor.validate_data(data):
            return data
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IDataExtractor(ABC):
    """
    Interface for data extraction operations.

    This interface ensures that all extractors follow the same contract,
    allowing for easy testing, mocking, and swapping of implementations.

    SOLID Principles Applied:
    - Single Responsibility: Only handles data extraction and validation
    - Open/Closed: Open for extension (new extractors), closed for modification
    - Liskov Substitution: All implementations can be used interchangeably
    - Interface Segregation: Minimal interface with only essential methods
    - Dependency Inversion: High-level modules depend on this abstraction, not concretions

    Contract:
    - extract(): MUST return list of dictionaries
    - validate_data(): SHOULD validate data structure

    Thread Safety:
    - Implementations are NOT required to be thread-safe
    - Caller should handle concurrency if needed
    """

    @abstractmethod
    def extract(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Extract data from the configured source.

        This method should handle:
        - Connection establishment
        - Data retrieval
        - Error handling with retries
        - Resource cleanup

        Args:
            **kwargs: Optional extraction parameters (e.g., filters, pagination)

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing extracted data.
                                 Empty list if no data found.

        Raises:
            ExtractionError: If extraction fails after all retries
            ConnectionError: If cannot connect to source
            ValidationError: If extracted data is invalid

        Example:
            >>> extractor = BreweryAPIExtractor(config)
            >>> data = extractor.extract(per_page=50, page=1)
            >>> print(f"Extracted {len(data)} records")

        Note:
            Implementations should log extraction progress and errors.
        """
        pass

    @abstractmethod
    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate the structure and quality of extracted data.

        This method should check:
        - Data is not empty (unless empty is expected)
        - Required fields are present
        - Data types are correct
        - Business rules are satisfied

        Args:
            data: Data to validate (typically from extract() method)

        Returns:
            bool: True if data is valid, False otherwise

        Note:
            If your extractor doesn't need validation, you can:
            1. Return True (accept all data)
            2. Perform basic checks (e.g., not empty)
            3. Implement full schema validation

            Consider logging validation failures for debugging.

        Example:
            >>> extractor = BreweryAPIExtractor(config)
            >>> data = extractor.extract()
            >>> if extractor.validate_data(data):
            ...     print("Data is valid!")
            ... else:
            ...     print("Validation failed!")
        """
        pass
