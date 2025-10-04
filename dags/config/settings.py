"""
Settings Module - Centralized Configuration

This module provides a centralized, type-safe configuration system following OOP principles:

SOLID Principles Applied:
- Single Responsibility: Each config class manages only its domain
- Open/Closed: Easy to extend with new config classes
- Liskov Substitution: All configs follow same pattern
- Interface Segregation: Separate configs per service
- Dependency Inversion: Configs injected, not hardcoded

Features:
- Encapsulation: Each service has its own configuration class
- Immutability: Configurations are frozen after initialization (frozen=True)
- Type Safety: Full type hints for IDE support and mypy
- Environment-Aware: Reads from environment variables with defaults
- Security: Safe __repr__ that doesn't expose secrets

Usage Examples:
    # Method 1: Direct instantiation
    from config import DatabricksConfig, AzureSQLConfig

    databricks = DatabricksConfig()
    print(databricks.cluster_id)  # Auto-loads from DATABRICKS_CLUSTER_ID env var

    # Method 2: Use singleton instances
    from config import databricks_config, azure_sql_config

    print(databricks_config.host)
    print(azure_sql_config.connection_string)

    # Method 3: Dependency Injection (recommended for DAGs)
    def my_dag_function(config: DatabricksConfig):
        # Config injected, easy to test with mocks
        return config.cluster_id

Configuration Loading Order:
1. Environment variables (.env file via os.getenv)
2. Default values (generic placeholders)
3. Airflow Variables (for production, optional)

Security Notes:
- Never commit .env file
- Use placeholders in defaults (XXXXX, your.email@example.com)
- __repr__ methods hide sensitive values (token='***')
- Use Airflow Connections for production deployments
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class DatabricksConfig:
    """
    Databricks Configuration.

    Encapsulates all Databricks-related settings with type safety.
    Reads from environment variables with sensible defaults.

    Attributes:
        host: Databricks workspace URL
        token: API token for authentication
        cluster_id: Default cluster ID for jobs
        job_id: Default job ID for operations
        notebook_path: Default notebook path
    """

    host: str = field(
        default_factory=lambda: os.getenv(
            "DATABRICKS_HOST", "https://adb-XXXXX.XX.azuredatabricks.net"
        )
    )

    token: str = field(
        default_factory=lambda: os.getenv(
            "DATABRICKS_TOKEN", "dapi********************************"
        )
    )

    cluster_id: str = field(
        default_factory=lambda: os.getenv(
            "DATABRICKS_CLUSTER_ID", "XXXX-XXXXXX-XXXXXXXX"
        )
    )

    job_id: str = field(
        default_factory=lambda: os.getenv("DATABRICKS_JOB_ID", "XXXXXXXXXXXXX")
    )

    notebook_path: str = field(
        default_factory=lambda: os.getenv(
            "DATABRICKS_NOTEBOOK_PATH",
            "/Workspace/Users/your.email@example.com/your_notebook",
        )
    )

    @property
    def connection_id(self) -> str:
        """Airflow connection ID for Databricks."""
        return "databricks_default"

    def __repr__(self) -> str:
        """Safe representation without exposing token."""
        return (
            f"DatabricksConfig(host='{self.host}', "
            f"cluster_id='{self.cluster_id}', "
            f"token='***')"
        )


@dataclass(frozen=True)
class AzureSQLConfig:
    """
    Azure SQL Database Configuration.

    Encapsulates Azure SQL connection settings.

    Attributes:
        server: SQL Server hostname
        database: Database name
        username: SQL username
        password: SQL password
        port: SQL Server port
        driver: ODBC driver name
    """

    server: str = field(
        default_factory=lambda: os.getenv(
            "AZURE_SQL_SERVER", "inbev-sql-server.database.windows.net"
        )
    )

    database: str = field(
        default_factory=lambda: os.getenv("AZURE_SQL_DATABASE", "inbev_db")
    )

    username: str = field(
        default_factory=lambda: os.getenv("AZURE_SQL_USERNAME", "inbev_admin")
    )

    password: str = field(
        default_factory=lambda: os.getenv("AZURE_SQL_PASSWORD", "YOUR_PASSWORD_HERE")
    )

    port: int = field(default_factory=lambda: int(os.getenv("AZURE_SQL_PORT", "1433")))

    driver: str = "ODBC Driver 18 for SQL Server"

    @property
    def connection_id(self) -> str:
        """Airflow connection ID for Azure SQL."""
        return "azure_sql_default"

    @property
    def connection_string(self) -> str:
        """
        Build ODBC connection string.

        Note: Prefer using Airflow Connections over this in production.
        """
        return (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"PORT={self.port};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=yes"
        )

    def __repr__(self) -> str:
        """Safe representation without exposing password."""
        return (
            f"AzureSQLConfig(server='{self.server}', "
            f"database='{self.database}', "
            f"password='***')"
        )


@dataclass(frozen=True)
class AzureDataFactoryConfig:
    """
    Azure Data Factory Configuration.

    Encapsulates ADF connection settings.

    Attributes:
        resource_group: Azure resource group name
        factory_name: Data Factory name
        pipeline_name: Default pipeline name
        tenant_id: Azure tenant ID
        subscription_id: Azure subscription ID
        client_id: Service principal client ID
        client_secret: Service principal secret
    """

    resource_group: str = field(
        default_factory=lambda: os.getenv("ADF_RESOURCE_GROUP", "inbev_resource_group")
    )

    factory_name: str = field(
        default_factory=lambda: os.getenv("ADF_FACTORY_NAME", "inbev-data-factory")
    )

    pipeline_name: str = field(
        default_factory=lambda: os.getenv("ADF_PIPELINE_NAME", "Pipeline1")
    )

    tenant_id: str = field(
        default_factory=lambda: os.getenv(
            "ADF_TENANT_ID", "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )
    )

    subscription_id: str = field(
        default_factory=lambda: os.getenv(
            "ADF_SUBSCRIPTION_ID", "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )
    )

    client_id: str = field(
        default_factory=lambda: os.getenv(
            "ADF_CLIENT_ID", "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )
    )

    client_secret: str = field(
        default_factory=lambda: os.getenv(
            "ADF_CLIENT_SECRET", "your_client_secret_here"
        )
    )

    @property
    def connection_id(self) -> str:
        """Airflow connection ID for Azure Data Factory."""
        return "azure_data_factory_default"

    def __repr__(self) -> str:
        """Safe representation without exposing secrets."""
        return (
            f"AzureDataFactoryConfig("
            f"factory='{self.factory_name}', "
            f"resource_group='{self.resource_group}', "
            f"client_secret='***')"
        )


@dataclass(frozen=True)
class APIConfig:
    """
    External APIs Configuration.

    Encapsulates external API endpoints and settings.
    """

    brewery_api_url: str = field(
        default_factory=lambda: os.getenv(
            "BREWERY_API_URL", "https://api.openbrewerydb.org/breweries"
        )
    )

    timeout: int = field(default_factory=lambda: int(os.getenv("API_TIMEOUT", "30")))

    retry_attempts: int = field(
        default_factory=lambda: int(os.getenv("API_RETRY_ATTEMPTS", "3"))
    )


@dataclass(frozen=True)
class AirflowConfig:
    """
    Airflow-specific Configuration.

    Encapsulates Airflow behavior settings.
    """

    default_retries: int = field(
        default_factory=lambda: int(os.getenv("AIRFLOW_DEFAULT_RETRIES", "2"))
    )

    retry_delay_seconds: int = field(
        default_factory=lambda: int(os.getenv("AIRFLOW_RETRY_DELAY", "300"))
    )

    email_on_failure: bool = field(
        default_factory=lambda: os.getenv("AIRFLOW_EMAIL_ON_FAILURE", "False").lower()
        == "true"
    )

    email_on_retry: bool = field(
        default_factory=lambda: os.getenv("AIRFLOW_EMAIL_ON_RETRY", "False").lower()
        == "true"
    )

    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    environment: str = field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )


# ==============================================================================
# Singleton Instances (Optional)
# ==============================================================================
# Pre-instantiated configuration objects for convenience.
# Use these when you don't need dependency injection or testing with mocks.
#
# Usage:
#     from config import databricks_config
#     print(databricks_config.host)
#
# Note: These load environment variables at module import time.
# ==============================================================================

azure_sql_config = AzureSQLConfig()
databricks_config = DatabricksConfig()
adf_config = AzureDataFactoryConfig()
api_config = APIConfig()
airflow_config = AirflowConfig()


# ==============================================================================
# Backward Compatibility
# ==============================================================================
# Alias for old code that imported "AzureConfig"
# DEPRECATED: Use AzureSQLConfig or AzureDataFactoryConfig explicitly instead
# ==============================================================================

AzureConfig = AzureSQLConfig  # Deprecated, use AzureSQLConfig
