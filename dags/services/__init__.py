"""
Services Module

Contains concrete implementations of ETL interfaces.

This module provides production-ready implementations of:
- IDataExtractor: Extract data from external sources
- IDataLoader: Load data into destinations
- IDataTransformer: Transform and clean data

SOLID Principles Applied:
- Single Responsibility: Each service has ONE job
- Dependency Injection: Services receive configs via constructor
- Liskov Substitution: Services implement interfaces and are interchangeable
- Open/Closed: Easy to extend without modifying existing code

Available Services:
- BreweryAPIExtractor: Extracts brewery data from Open Brewery DB API
- AzureSQLLoader: Loads data into Azure SQL Database
- BreweryTransformer: Transforms and cleans brewery data

Usage:
    from services import BreweryAPIExtractor, AzureSQLLoader, BreweryTransformer
    from config import APIConfig, AzureSQLConfig

    # Create services with dependency injection
    extractor = BreweryAPIExtractor(APIConfig())
    transformer = BreweryTransformer()
    loader = AzureSQLLoader(AzureSQLConfig(), table_name="Breweries")

    # ETL pipeline
    raw_data = extractor.extract()
    clean_data = transformer.transform(raw_data)
    count = loader.load(clean_data)

Best Practice:
Use ETLFactory to create services instead of direct instantiation.
See: factories/etl_factory.py

See Also:
- interfaces/: Abstract interfaces that services implement
- factories/: Factory methods for creating services
- README.md: Detailed documentation
"""

from .brewery_api_extractor import BreweryAPIExtractor
from .azure_sql_loader import AzureSQLLoader
from .brewery_transformer import BreweryTransformer

__all__ = [
    "BreweryAPIExtractor",
    "AzureSQLLoader",
    "BreweryTransformer",
]
