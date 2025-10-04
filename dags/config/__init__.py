"""
Configuration Module

Provides centralized configuration management for all DAGs.

All configuration classes follow SOLID principles:
- Immutable (frozen dataclasses)
- Type-safe (full type hints)
- Encapsulated (domain-specific configs)
- Environment-aware (reads from .env)
"""

from .settings import (
    # Main configuration classes
    AzureSQLConfig,
    AzureDataFactoryConfig,
    DatabricksConfig,
    AirflowConfig,
    APIConfig,
    # Singleton instances (optional)
    azure_sql_config,
    adf_config,
    databricks_config,
    airflow_config,
    api_config,
    # Backward compatibility alias
    AzureConfig,
)

__all__ = [
    # Configuration classes
    "AzureSQLConfig",
    "AzureDataFactoryConfig",
    "DatabricksConfig",
    "AirflowConfig",
    "APIConfig",
    # Singleton instances
    "azure_sql_config",
    "adf_config",
    "databricks_config",
    "airflow_config",
    "api_config",
    # Alias (deprecated, use AzureSQLConfig instead)
    "AzureConfig",
]

