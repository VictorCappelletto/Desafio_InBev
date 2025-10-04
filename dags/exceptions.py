"""
Custom Exceptions - SOLID Architecture

Defines specific exceptions for better error handling and debugging.
Implements hierarchy of exceptions following inheritance principles.

SOLID Principles Applied:
- Single Responsibility: Each exception type has one specific purpose
- Open/Closed: Easy to add new exception types without modifying existing ones
- Liskov Substitution: All exceptions can be used interchangeably where BaseETLException is expected
- Dependency Inversion: Code depends on exception types, not concrete implementations

Exception Hierarchy:
    BaseETLException (base)
    ├── ExtractionError (data extraction failures)
    ├── TransformationError (data transformation failures)
    ├── LoadError (data loading failures)
    ├── ValidationError (data validation failures)
    ├── ConfigurationError (configuration issues)
    └── ConnectionError (external service connection failures)

Benefits:
- Type-safe error handling
- Rich error context with details dict
- Professional error messages
- Easy to catch specific errors
- Better debugging with context

Usage:
    from exceptions import ExtractionError, ValidationError
    
    # Raise with message only
    raise ExtractionError("Failed to extract data from API")
    
    # Raise with details for context
    raise ExtractionError(
        "Failed to extract data from API",
        details={"url": "https://api.example.com", "status_code": 500}
    )
    
    # Catch specific exceptions
    try:
        data = extractor.extract()
    except ExtractionError as e:
        logger.error(f"Extraction failed: {e}")
        logger.debug(f"Error details: {e.details}")

See Also:
    - services/: Uses these exceptions for error handling
    - utils/logger.py: Logs these exceptions with context
"""

from typing import Dict, Optional, Any


__all__ = [
    "BaseETLException",
    "ExtractionError",
    "TransformationError",
    "LoadError",
    "ValidationError",
    "ConfigurationError",
    "ConnectionError",
]


class BaseETLException(Exception):
    """
    Base exception for all ETL operations.
    
    Provides a common interface for all ETL-related exceptions with support
    for rich error context through the details dictionary. All custom exceptions
    in this module inherit from this base class.
    
    Attributes:
        message (str): Human-readable error message
        details (Dict[str, Any]): Additional context about the error
    
    Args:
        message: Description of what went wrong
        details: Optional dict with additional error context (e.g., URLs, IDs, status codes)
    
    Examples:
        Basic usage:
            >>> raise BaseETLException("Something went wrong")
        
        With details:
            >>> raise BaseETLException(
            ...     "API call failed",
            ...     details={"url": "https://api.example.com", "status_code": 500}
            ... )
        
        Accessing details:
            >>> try:
            ...     raise BaseETLException("Error", details={"id": 123})
            ... except BaseETLException as e:
            ...     print(e.details["id"])  # 123
    
    Note:
        This is the base exception. In most cases, you should use one of the
        specific exception types (ExtractionError, LoadError, etc.) instead.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """
        Return string representation with details.
        
        Returns:
            str: Formatted error message with details if available
        
        Examples:
            >>> e = BaseETLException("Error", details={"code": 500})
            >>> str(e)
            'Error | Details: code=500'
        """
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} | Details: {details_str}"
        return self.message
    
    def __repr__(self) -> str:
        """
        Return detailed representation for debugging.
        
        Returns:
            str: Class name with message and details
        
        Examples:
            >>> e = BaseETLException("Error", details={"id": 123})
            >>> repr(e)
            "BaseETLException('Error', details={'id': 123})"
        """
        return f"{self.__class__.__name__}('{self.message}', details={self.details})"


class ExtractionError(BaseETLException):
    """
    Raised when data extraction fails.
    
    Use this exception when:
    - API requests fail
    - File reading errors occur
    - Database queries fail during extraction
    - Data source is unavailable
    
    Examples:
        >>> raise ExtractionError("API request failed", details={"url": "...", "status": 500})
        >>> raise ExtractionError("File not found", details={"path": "/data/breweries.csv"})
    
    See Also:
        - services.brewery_api_extractor: Uses this for API failures
    """
    pass


class TransformationError(BaseETLException):
    """
    Raised when data transformation fails.
    
    Use this exception when:
    - Data validation during transformation fails
    - Type conversion errors occur
    - Required fields are missing
    - Data format is incorrect
    
    Examples:
        >>> raise TransformationError("Invalid data format", details={"field": "brewery_type"})
        >>> raise TransformationError("Type conversion failed", details={"value": "abc", "expected_type": "int"})
    
    See Also:
        - services.brewery_transformer: Uses this for transformation failures
    """
    pass


class LoadError(BaseETLException):
    """
    Raised when data loading fails.
    
    Use this exception when:
    - Database insert/update operations fail
    - File writing errors occur
    - Connection to destination is lost
    - Transaction rollback occurs
    
    Examples:
        >>> raise LoadError("Database insert failed", details={"table": "Breweries", "rows": 100})
        >>> raise LoadError("Connection lost", details={"server": "sql-server.database.windows.net"})
    
    See Also:
        - services.azure_sql_loader: Uses this for database load failures
    """
    pass


class ValidationError(BaseETLException):
    """
    Raised when data validation fails.
    
    Use this exception when:
    - Data quality checks fail
    - Schema validation fails
    - Business rules are violated
    - Data integrity checks fail
    
    Examples:
        >>> raise ValidationError("Row count too low", details={"actual": 50, "expected_min": 100})
        >>> raise ValidationError("Duplicate IDs found", details={"duplicate_count": 5})
    
    See Also:
        - data_quality_check_dag.py: Uses this for quality check failures
    """
    pass


class ConfigurationError(BaseETLException):
    """
    Raised when configuration is invalid.
    
    Use this exception when:
    - Required environment variables are missing
    - Configuration values are invalid
    - Credentials are missing or incorrect
    - Connection strings are malformed
    
    Examples:
        >>> raise ConfigurationError("Missing API key", details={"env_var": "API_KEY"})
        >>> raise ConfigurationError("Invalid timeout value", details={"value": -1, "expected": ">0"})
    
    See Also:
        - config/settings.py: Configuration validation
        - DAGs validation tasks: Pre-flight configuration checks
    """
    pass


class ConnectionError(BaseETLException):
    """
    Raised when connection to external service fails.
    
    Use this exception when:
    - Network connection fails
    - Service is unavailable
    - Authentication fails
    - Timeout occurs
    
    Examples:
        >>> raise ConnectionError("Database connection failed", details={"server": "sql-server", "timeout": 30})
        >>> raise ConnectionError("API authentication failed", details={"url": "...", "status": 401})
    
    Note:
        This is different from Python's built-in ConnectionError.
        Import as: from exceptions import ConnectionError
    
    See Also:
        - services.azure_sql_loader: Database connection handling
        - services.brewery_api_extractor: API connection handling
    """
    pass

