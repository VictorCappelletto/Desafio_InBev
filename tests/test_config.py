"""
Unit Tests for Configuration Classes

Tests the config dataclasses to ensure they work correctly.
"""

import os

# Add dags to path
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dags"))

from config.settings import (
    AirflowConfig,
    APIConfig,
    AzureDataFactoryConfig,
    AzureSQLConfig,
    DatabricksConfig,
)


class TestDatabricksConfig:
    """Test Databricks configuration."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = DatabricksConfig()

        assert config.host is not None
        assert config.token is not None
        assert config.cluster_id is not None
        assert config.job_id is not None
        assert config.notebook_path is not None

    def test_connection_id_property(self):
        """Test connection_id property."""
        config = DatabricksConfig()
        assert config.connection_id == "databricks_default"

    def test_repr_hides_token(self):
        """Test that __repr__ doesn't expose token."""
        config = DatabricksConfig()
        repr_str = repr(config)

        assert "token='***'" in repr_str
        assert config.token not in repr_str

    @patch.dict(
        os.environ,
        {
            "DATABRICKS_HOST": "https://test.databricks.net",
            "DATABRICKS_TOKEN": "dapi_test_token",
            "DATABRICKS_CLUSTER_ID": "test-cluster-123",
        },
    )
    def test_environment_variables(self):
        """Test that environment variables are read correctly."""
        config = DatabricksConfig()

        assert config.host == "https://test.databricks.net"
        assert config.token == "dapi_test_token"
        assert config.cluster_id == "test-cluster-123"


class TestAzureSQLConfig:
    """Test Azure SQL configuration."""

    def test_default_values(self):
        """Test default values."""
        config = AzureSQLConfig()

        assert config.server is not None
        assert config.database is not None
        assert config.username is not None
        assert config.port == 1433
        assert config.driver == "ODBC Driver 18 for SQL Server"

    def test_connection_id_property(self):
        """Test connection_id property."""
        config = AzureSQLConfig()
        assert config.connection_id == "azure_sql_default"

    def test_connection_string_format(self):
        """Test connection string generation."""
        config = AzureSQLConfig()
        conn_str = config.connection_string

        assert "DRIVER={ODBC Driver 18 for SQL Server}" in conn_str
        assert f"SERVER={config.server}" in conn_str
        assert f"DATABASE={config.database}" in conn_str
        assert "TrustServerCertificate=yes" in conn_str
        assert "Encrypt=yes" in conn_str

    def test_repr_hides_password(self):
        """Test that __repr__ doesn't expose password."""
        config = AzureSQLConfig()
        repr_str = repr(config)

        assert "password='***'" in repr_str
        assert config.password not in repr_str


class TestAPIConfig:
    """Test API configuration."""

    def test_default_values(self):
        """Test default values."""
        config = APIConfig()

        assert config.brewery_api_url is not None
        assert config.timeout > 0
        assert config.retry_attempts > 0

    @patch.dict(
        os.environ,
        {
            "BREWERY_API_URL": "https://test-api.com",
            "API_TIMEOUT": "60",
            "API_RETRY_ATTEMPTS": "5",
        },
    )
    def test_environment_variables(self):
        """Test environment variable overrides."""
        config = APIConfig()

        assert config.brewery_api_url == "https://test-api.com"
        assert config.timeout == 60
        assert config.retry_attempts == 5


class TestAirflowConfig:
    """Test Airflow configuration."""

    def test_default_values(self):
        """Test default values."""
        config = AirflowConfig()

        assert config.default_retries >= 0
        assert config.retry_delay_seconds > 0
        assert isinstance(config.email_on_failure, bool)
        assert isinstance(config.email_on_retry, bool)
        assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    @patch.dict(
        os.environ,
        {
            "AIRFLOW_DEFAULT_RETRIES": "3",
            "AIRFLOW_RETRY_DELAY": "600",
            "AIRFLOW_EMAIL_ON_FAILURE": "True",
            "LOG_LEVEL": "DEBUG",
            "ENVIRONMENT": "production",
        },
    )
    def test_environment_variables(self):
        """Test environment variable overrides."""
        config = AirflowConfig()

        assert config.default_retries == 3
        assert config.retry_delay_seconds == 600
        assert config.email_on_failure is True
        assert config.log_level == "DEBUG"
        assert config.environment == "production"


class TestConfigImmutability:
    """Test that configs are immutable (frozen)."""

    def test_databricks_config_frozen(self):
        """Test that DatabricksConfig is frozen."""
        config = DatabricksConfig()

        with pytest.raises(Exception):  # FrozenInstanceError
            config.host = "https://new-host.com"

    def test_azure_sql_config_frozen(self):
        """Test that AzureSQLConfig is frozen."""
        config = AzureSQLConfig()

        with pytest.raises(Exception):
            config.server = "new-server.com"
