"""
Data Loader Interface

Defines the contract for all data loading operations.

This interface follows SOLID principles, particularly:
- Dependency Inversion Principle (DIP): High-level code depends on this abstraction
- Liskov Substitution Principle (LSP): All implementations are interchangeable
- Interface Segregation Principle (ISP): Minimal, focused interface

Design Notes:
- load() is the core method - all loaders MUST implement
- create_table_if_not_exists() is optional for database loaders
- Non-database loaders (S3, File, API) can implement as no-op
- Future: Consider separating table operations into DatabaseLoader subclass

Examples:
    # Database loader
    class SQLLoader(IDataLoader):
        def load(self, data):
            return self._insert_to_database(data)
        
        def create_table_if_not_exists(self):
            self._execute_create_table_sql()
    
    # File loader (no table creation needed)
    class FileLoader(IDataLoader):
        def load(self, data):
            return self._write_to_file(data)
        
        def create_table_if_not_exists(self):
            pass  # No-op for file loaders
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IDataLoader(ABC):
    """
    Interface for data loading operations.
    
    This interface ensures that all loaders follow the same contract,
    allowing for easy testing, mocking, and swapping of implementations.
    
    SOLID Principles Applied:
    - Single Responsibility: Only handles data loading to destination
    - Open/Closed: Open for extension (new loaders), closed for modification
    - Liskov Substitution: All implementations can be used interchangeably
    - Interface Segregation: Minimal interface (consider: table ops might be too specific)
    - Dependency Inversion: High-level modules depend on this abstraction, not concretions
    
    Contract:
    - load(): MUST load data and return count
    - create_table_if_not_exists(): MAY be no-op for non-database loaders
    
    Thread Safety:
    - Implementations are NOT required to be thread-safe
    - Caller should handle concurrency if needed
    
    Note on Interface Segregation:
    The `create_table_if_not_exists` method may violate ISP for non-database loaders.
    Consider implementing as no-op if not applicable to your loader type.
    """
    
    @abstractmethod
    def load(self, data: List[Dict[str, Any]], **kwargs: Any) -> int:
        """
        Load data to the configured destination.
        
        This method should handle:
        - Connection/file handling
        - Data insertion/writing
        - Error handling with retries
        - Transaction management (if applicable)
        - Resource cleanup
        
        Args:
            data: List of dictionaries containing data to load.
                 Each dict represents one record.
            **kwargs: Optional loading parameters (e.g., batch_size, mode='append'/'overwrite')
        
        Returns:
            int: Number of records successfully loaded.
                 Should be equal to len(data) if all succeeded.
            
        Raises:
            LoadError: If loading fails after all retries
            ConnectionError: If cannot connect to destination
            ValidationError: If data fails destination constraints
            
        Example:
            >>> loader = AzureSQLLoader(config)
            >>> count = loader.load(data, batch_size=1000)
            >>> print(f"Loaded {count}/{len(data)} records")
        
        Note:
            Implementations should:
            - Log loading progress
            - Use transactions when possible
            - Handle duplicates appropriately (upsert vs insert)
            - Return actual count of loaded records
        """
        pass
    
    @abstractmethod
    def create_table_if_not_exists(self) -> None:
        """
        Create destination table/structure if it doesn't exist.
        
        This method is primarily for database loaders. Non-database loaders
        (e.g., FileLoader, S3Loader, APILoader) should implement as no-op.
        
        For database loaders, this method should:
        - Check if table/schema exists
        - Create table with appropriate schema
        - Create necessary indexes
        - Handle errors gracefully
        
        Raises:
            LoadError: If table creation fails
            
        Example:
            >>> loader = AzureSQLLoader(config, table_name="Breweries")
            >>> loader.create_table_if_not_exists()  # Creates table if needed
            >>> loader.load(data)  # Now safe to load
        
        Note:
            Non-database loaders can implement as:
            ```python
            def create_table_if_not_exists(self):
                pass  # No-op for file/S3/API loaders
            ```
            
            This method may violate ISP. Future refactor could separate
            database-specific operations into IDatabaseLoader interface.
        """
        pass

