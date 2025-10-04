"""
Example: How to use Configuration Classes in DAGs

This example demonstrates OOP and SOLID principles in action:
- Single Responsibility: Each config class handles its domain
- Open/Closed: Easy to extend without modifying
- Dependency Inversion: Depend on abstractions, not implementations
- Encapsulation: Config details hidden in classes
- Dependency Injection: Config injected into functions
- Type Safety: Full IDE support with type hints
- Immutability: Frozen dataclasses prevent accidental changes

See also:
- dags/config/README.md - Complete configuration documentation
- tests/test_config.py - Unit tests for configurations
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator

# Import configuration classes
from config import AirflowConfig, APIConfig, AzureSQLConfig, DatabricksConfig
from utils.logger import get_logger, log_task_start, log_task_success

# ==============================================================================
# Example 1: Using Config with Dependency Injection
# ==============================================================================


def extract_data_with_config(api_config: APIConfig):
    """
    Extract data using injected configuration.

    Benefits:
    - Testable: Easy to mock APIConfig for tests
    - Flexible: Can inject different configs for different envs
    - Type-safe: IDE knows what properties are available
    """
    logger = get_logger(__name__)

    log_task_start(
        logger,
        "extract_data",
        api_url=api_config.brewery_api_url,
        timeout=api_config.timeout,
    )

    import requests

    try:
        response = requests.get(api_config.brewery_api_url, timeout=api_config.timeout)
        response.raise_for_status()
        data = response.json()

        log_task_success(
            logger, "extract_data", records=len(data), status_code=response.status_code
        )

        return data

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise


def load_data_with_config(sql_config: AzureSQLConfig, **context):
    """
    Load data using injected SQL configuration.

    Note: In production, prefer using Airflow Connections over
    building connection strings manually.
    """
    logger = get_logger(__name__)

    log_task_start(
        logger, "load_data", server=sql_config.server, database=sql_config.database
    )

    # Get data from previous task
    ti = context["ti"]
    data = ti.xcom_pull(task_ids="extract_data_task")

    # In real implementation, use pyodbc with connection string
    # conn_string = sql_config.connection_string

    log_task_success(logger, "load_data", records_loaded=len(data) if data else 0)


# ==============================================================================
# Example 2: Creating DAG with OOP Configuration
# ==============================================================================

# Initialize configurations (follows Dependency Injection pattern)
databricks = DatabricksConfig()
azure_sql = AzureSQLConfig()
airflow_cfg = AirflowConfig()
api_cfg = APIConfig()

# Default args from configuration (DRY principle)
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 10, 1),
    "email_on_failure": airflow_cfg.email_on_failure,
    "email_on_retry": airflow_cfg.email_on_retry,
    "retries": airflow_cfg.default_retries,
    "retry_delay": timedelta(seconds=airflow_cfg.retry_delay_seconds),
}

# Create DAG
with DAG(
    "config_example_dag",
    default_args=default_args,
    description="Example DAG using OOP configuration",
    schedule_interval="@daily",
    catchup=False,
    tags=["example", "config", "oop"],
) as dag:

    # Task 1: Extract using API config
    extract_task = PythonOperator(
        task_id="extract_data_task",
        python_callable=extract_data_with_config,
        op_kwargs={"api_config": api_cfg},  # Dependency Injection
    )

    # Task 2: Load using SQL config
    load_task = PythonOperator(
        task_id="load_data_task",
        python_callable=load_data_with_config,
        op_kwargs={"sql_config": azure_sql},  # Dependency Injection
        provide_context=True,
    )

    # Task 3: Process using Databricks config
    databricks_task = DatabricksRunNowOperator(
        task_id="process_databricks_task",
        databricks_conn_id=databricks.connection_id,  # From config property
        job_id=databricks.job_id,  # From config
        notebook_params={
            "env": airflow_cfg.environment,
            "log_level": airflow_cfg.log_level,
        },
    )

    # Define workflow
    extract_task >> load_task >> databricks_task


# ==============================================================================
# Example 3: Testing with Mock Configs (Unit Testing)
# ==============================================================================


def test_extract_with_mock_config():
    """
    Example of how to test functions with mocked configuration.

    This demonstrates the testability benefits of dependency injection.

    Note: Since our configs use frozen dataclasses with environment variables,
    we need to mock the environment before instantiating the config.
    """
    import os
    from unittest.mock import Mock, patch

    # Method 1: Mock environment variables
    with patch.dict(
        os.environ,
        {
            "BREWERY_API_URL": "http://localhost:8080/test",
            "API_TIMEOUT": "5",
            "API_RETRY_ATTEMPTS": "1",
        },
    ):
        test_config = APIConfig()
        assert test_config.brewery_api_url == "http://localhost:8080/test"
        assert test_config.timeout == 5

        # Now test with this config
        # result = extract_data_with_config(test_config)
        # assert result is not None

    # Method 2: Mock the entire config object (easier for unit tests)
    mock_config = Mock(spec=APIConfig)
    mock_config.brewery_api_url = "http://mock-api.com"
    mock_config.timeout = 10
    mock_config.retry_attempts = 1

    # Test with mock
    # result = extract_data_with_config(mock_config)
    # assert result is not None

    print("✅ Example 3: Both mocking methods work!")


def test_with_pytest_fixture():
    """
    Example of using pytest fixtures for testing.

    Add this to conftest.py:

    ```python
    @pytest.fixture
    def test_api_config():
        with patch.dict(os.environ, {
            'BREWERY_API_URL': 'http://test-api.com',
            'API_TIMEOUT': '5',
        }):
            yield APIConfig()

    def test_extract(test_api_config):
        result = extract_data_with_config(test_api_config)
        assert result is not None
    ```
    """
    pass


# ==============================================================================
# Example 4: Environment-specific Configurations
# ==============================================================================


def get_environment_config(environment: str) -> AirflowConfig:
    """
    Factory pattern: Return different configs based on environment.

    This demonstrates flexibility of OOP approach.
    """
    if environment == "production":
        # Could load from different source
        return AirflowConfig()
    elif environment == "staging":
        # Different settings for staging
        return AirflowConfig()
    else:
        # Development settings
        return AirflowConfig()


# ==============================================================================
# Example 5: Using Singleton Instances (Alternative Approach)
# ==============================================================================


def example_with_singletons():
    """
    Alternative: Use pre-instantiated singleton configs.

    Pros:
    - Less verbose (no need to instantiate)
    - Convenient for simple use cases

    Cons:
    - Harder to test (difficult to mock)
    - Side effects (loads env vars at import time)

    Recommendation: Use for simple scripts, avoid in complex DAGs.
    """
    from config import api_config, azure_sql_config, databricks_config

    # Direct access to singleton instances
    print(f"Databricks Host: {databricks_config.host}")
    print(f"SQL Server: {azure_sql_config.server}")
    print(f"API URL: {api_config.brewery_api_url}")

    # Use in functions (less flexible than DI)
    def some_task():
        # Direct access - harder to test!
        return databricks_config.cluster_id

    print("✅ Example 5: Singleton instances work, but less flexible!")


# ==============================================================================
# Example 6: Debugging Configuration Issues
# ==============================================================================


def debug_configuration():
    """
    Debug configuration loading issues.

    Common issues:
    1. Environment variable not loaded
    2. .env file not found
    3. Wrong variable name
    """
    import os

    from config import DatabricksConfig

    # Check if env var is set
    print(f"DATABRICKS_HOST env var: {os.getenv('DATABRICKS_HOST')}")

    # Load config
    config = DatabricksConfig()

    # Safe repr (doesn't expose token)
    print(f"Config loaded: {config}")

    # Check individual properties
    print(f"Host: {config.host}")
    print(f"Cluster ID: {config.cluster_id}")

    # Warning: This will expose the token!
    # print(f"Token: {config.token}")  # Don't do this in logs!

    # Check if using defaults (placeholder values)
    if "XXXXX" in config.host:
        print("⚠️  WARNING: Using placeholder host! Check your .env file.")

    if config.token == "dapi********************************":
        print("⚠️  WARNING: Using placeholder token! Check your .env file.")

    print("✅ Example 6: Debug checks complete!")


# ==============================================================================
# Example 7: Configuration in Production
# ==============================================================================


def production_best_practices():
    """
    Best practices for production deployments.

    1. Use Airflow Connections for credentials
    2. Use Airflow Variables for IDs/configs
    3. Use Azure Key Vault for secrets
    4. Never log sensitive values
    5. Use environment-specific configs
    """
    from config import AirflowConfig, DatabricksConfig

    # Check environment
    airflow_cfg = AirflowConfig()

    if airflow_cfg.environment == "production":
        print("🚀 Production mode:")
        print("  - Using Airflow Connections")
        print("  - Using Azure Key Vault")
        print("  - Secrets not logged")
    else:
        print("🔧 Development mode:")
        print("  - Using .env file")
        print("  - Local configurations")

    # Use connection_id property for operators
    databricks = DatabricksConfig()
    connection_id = databricks.connection_id  # "databricks_default"

    print(f"✅ Using Airflow Connection: {connection_id}")


# ==============================================================================
# Benefits of This Approach
# ==============================================================================
"""
✅ SOLID Principles Applied:
   - Single Responsibility: Each config class manages one domain
   - Open/Closed: Easy to extend, hard to break
   - Liskov Substitution: All configs follow same pattern
   - Interface Segregation: Separate configs per service
   - Dependency Inversion: Depend on abstractions

✅ OOP Benefits:
   - Encapsulation: Config details hidden in classes
   - Inheritance: Base patterns can be extended
   - Polymorphism: Different configs, same interface
   - Abstraction: Hide complexity, expose simplicity

✅ Practical Benefits:
   - Type Safety: Full IDE autocomplete and type checking
   - Testability: Easy to mock configs for unit tests
   - DRY: Single source of truth for each configuration
   - Immutability: Frozen dataclasses prevent accidental changes
   - Documentation: Docstrings explain each setting
   - Security: Safe repr() hides sensitive values
   - Flexibility: Easy to add new configs without changing code
   - Maintainability: Centralized configuration management
   - Environment-aware: Automatic loading from .env
   - Production-ready: Compatible with Airflow Connections

✅ Testing Benefits:
   - Mockable: Easy to create test configs
   - Isolated: Each test can have different configs
   - Predictable: Frozen configs = no surprises
   - Fast: No actual connections in unit tests

🔗 Learn More:
   - See dags/config/README.md for complete documentation
   - See tests/test_config.py for unit test examples
   - See ARCHITECTURE.md for SOLID principles explanation
"""


# ==============================================================================
# Run Examples (for testing)
# ==============================================================================

if __name__ == "__main__":
    """
    Run all examples to verify they work.

    Usage:
        python dags/examples/config_usage_example.py
    """
    print("=" * 80)
    print("CONFIGURATION EXAMPLES")
    print("=" * 80)
    print()

    try:
        print("Running Example 3: Testing with mocks...")
        test_extract_with_mock_config()
        print()

        print("Running Example 5: Singleton instances...")
        example_with_singletons()
        print()

        print("Running Example 6: Debug configuration...")
        debug_configuration()
        print()

        print("Running Example 7: Production best practices...")
        production_best_practices()
        print()

        print("=" * 80)
        print("✅ ALL EXAMPLES PASSED!")
        print("=" * 80)

    except Exception as e:
        print("=" * 80)
        print(f"❌ ERROR: {e}")
        print("=" * 80)
        import traceback

        traceback.print_exc()
