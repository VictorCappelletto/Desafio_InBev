"""
Brewery ETL DAG - SOLID Architecture

This DAG demonstrates professional software engineering principles:

SOLID Principles Applied:
- Single Responsibility: Each class/function has one clear purpose
- Open/Closed: Easy to extend without modifying existing code
- Liskov Substitution: Interfaces allow swapping implementations
- Interface Segregation: Focused, minimal interfaces
- Dependency Inversion: Depends on abstractions, not concretions

Additional Patterns:
- Dependency Injection: Configurations injected into services
- Factory Pattern: Centralized object creation
- Strategy Pattern: Different extractors/loaders can be swapped
- Exception Handling: Custom exceptions for better error tracking
- Logging: Structured, professional logging
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from airflow import DAG
from airflow.operators.python import PythonOperator

# Configuration
from config import AirflowConfig, APIConfig, AzureSQLConfig

# Exceptions
from exceptions import ExtractionError, LoadError, TransformationError

# Factories
from factories import ETLFactory

# Logging
from utils import get_logger, log_task_error, log_task_start, log_task_success

# ==============================================================================
# Initialize Configuration (Dependency Injection)
# ==============================================================================

airflow_config = AirflowConfig()
api_config = APIConfig()
sql_config = AzureSQLConfig()

logger = get_logger(__name__)


# ==============================================================================
# ETL Functions (Pure Functions with Dependency Injection)
# ==============================================================================


def extract_brewery_data(**context: Any) -> None:
    """
    Extract brewery data from API.

    Orchestrates the extraction of brewery data from Open Brewery DB API
    using the Factory Pattern and Dependency Injection.

    Args:
        **context: Airflow task context

    Raises:
        ExtractionError: If data extraction fails

    This function demonstrates:
    - Dependency Injection: Uses injected configuration
    - Single Responsibility: Only handles extraction orchestration
    - Error Handling: Proper exception handling
    - XCom: Shares data between tasks
    - Factory Pattern: Uses ETLFactory for object creation
    """
    log_task_start(logger, "extract_brewery_data", source="Open Brewery API")

    try:
        # Use factory to create extractor (Factory Pattern)
        extractor = ETLFactory.create_brewery_extractor(api_config)

        # Extract data (Strategy Pattern - can swap extractors)
        data = extractor.extract()

        # Push to XCom for next task
        ti = context["ti"]
        ti.xcom_push(key="raw_data", value=data)

        log_task_success(
            logger,
            "extract_brewery_data",
            records=len(data),
            source=api_config.brewery_api_url,
        )

    except ExtractionError as e:
        log_task_error(logger, "extract_brewery_data", e)
        raise


def transform_brewery_data(**context: Any) -> None:
    """
    Transform brewery data.

    Applies data transformations to prepare brewery data for loading into
    Azure SQL Database. Handles data cleaning, normalization, and type conversion.

    Args:
        **context: Airflow task context

    Raises:
        TransformationError: If data transformation fails

    Demonstrates:
    - Pure function with no side effects (functional programming)
    - Clear input/output via XCom
    - Error propagation
    - Factory Pattern: Uses ETLFactory for transformer creation
    """
    log_task_start(logger, "transform_brewery_data")

    try:
        # Get data from previous task
        ti = context["ti"]
        raw_data = ti.xcom_pull(task_ids="extract_task", key="raw_data")

        if not raw_data:
            logger.warning("No data to transform")
            return

        # Use factory to create transformer
        transformer = ETLFactory.create_brewery_transformer()

        # Transform data
        transformed_data = transformer.transform(raw_data)

        # Push to XCom
        ti.xcom_push(key="transformed_data", value=transformed_data)

        log_task_success(
            logger,
            "transform_brewery_data",
            records_in=len(raw_data),
            records_out=len(transformed_data),
        )

    except TransformationError as e:
        log_task_error(logger, "transform_brewery_data", e)
        raise


def load_brewery_data(**context: Any) -> None:
    """
    Load brewery data to Azure SQL Database.

    Loads transformed brewery data into Azure SQL Database using MERGE (upsert)
    operation to handle duplicates. Creates the table if it doesn't exist.

    Args:
        **context: Airflow task context

    Raises:
        LoadError: If data loading fails

    Demonstrates:
    - Resource management (connections)
    - Atomic operations
    - Error handling with rollback
    - Factory Pattern: Uses ETLFactory with table_name configuration
    - UPSERT operations: MERGE for handling duplicates
    """
    log_task_start(logger, "load_brewery_data", destination="Azure SQL")

    try:
        # Get data from previous task
        ti = context["ti"]
        transformed_data = ti.xcom_pull(
            task_ids="transform_task", key="transformed_data"
        )

        if not transformed_data:
            logger.warning("No data to load")
            return

        # Use factory to create loader with table name
        loader = ETLFactory.create_azure_sql_loader(sql_config, table_name="Breweries")

        # Create table if needed
        loader.create_table_if_not_exists()

        # Load data
        loaded_count = loader.load(transformed_data)

        log_task_success(
            logger,
            "load_brewery_data",
            records_loaded=loaded_count,
            records_attempted=len(transformed_data),
            success_rate=f"{(loaded_count/len(transformed_data)*100):.1f}%",
            destination=f"{sql_config.server}/{sql_config.database}",
            table="Breweries",
        )

    except LoadError as e:
        log_task_error(logger, "load_brewery_data", e)
        raise


# ==============================================================================
# DAG Definition (Configuration-Driven)
# ==============================================================================

# Build default_args from configuration (DRY Principle)
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 10, 1),
    "email_on_failure": airflow_config.email_on_failure,
    "email_on_retry": airflow_config.email_on_retry,
    "retries": airflow_config.default_retries,
    "retry_delay": timedelta(seconds=airflow_config.retry_delay_seconds),
}

# Create DAG
with DAG(
    "brewery_etl_solid",
    default_args=default_args,
    description="Extract brewery data from API and load to Azure SQL (SOLID Architecture)",
    schedule_interval="@daily",
    catchup=False,
    tags=["etl", "brewery", "azure-sql", "solid", "production"],
) as dag:

    # Task 1: Extract
    extract_task = PythonOperator(
        task_id="extract_task",
        python_callable=extract_brewery_data,
        provide_context=True,
        doc_md="""
        ### Extract Brewery Data
        
        Extracts brewery data from Open Brewery DB API.
        
        **Architecture:**
        - Uses `BreweryAPIExtractor` (implements `IDataExtractor`)
        - Configuration via `APIConfig`
        - Retry logic with exponential backoff
        - Data validation before passing to next task
        
        **Output:** Raw brewery data in XCom
        """,
    )

    # Task 2: Transform
    transform_task = PythonOperator(
        task_id="transform_task",
        python_callable=transform_brewery_data,
        provide_context=True,
        doc_md="""
        ### Transform Brewery Data
        
        Transforms raw brewery data for SQL loading.
        
        **Architecture:**
        - Uses `BreweryTransformer` (implements `IDataTransformer`)
        - Normalizes data types
        - Handles null values
        - Truncates strings to schema limits
        
        **Input:** Raw data from extract_task
        **Output:** Transformed data in XCom
        """,
    )

    # Task 3: Load
    load_task = PythonOperator(
        task_id="load_task",
        python_callable=load_brewery_data,
        provide_context=True,
        doc_md="""
        ### Load Brewery Data
        
        Loads transformed data to Azure SQL Database.
        
        **Architecture:**
        - Uses `AzureSQLLoader` (implements `IDataLoader`)
        - Configuration via `AzureSQLConfig`
        - MERGE operation (upsert) to handle duplicates
        - Transaction management
        - Connection pooling
        
        **Input:** Transformed data from transform_task
        **Output:** Data loaded to Azure SQL
        """,
    )

    # Define workflow (ETL Pipeline)
    extract_task >> transform_task >> load_task


# ==============================================================================
# Benefits of This Architecture
# ==============================================================================
"""
✅ TESTABILITY: Each component can be unit tested in isolation
✅ MAINTAINABILITY: Clear separation of concerns
✅ EXTENSIBILITY: Easy to add new extractors/loaders
✅ REUSABILITY: Services can be reused in other DAGs
✅ READABILITY: Self-documenting code with clear structure
✅ SECURITY: Configurations separated from code
✅ PROFESSIONALISM: Industry-standard patterns
✅ SCALABILITY: Easy to scale individual components
✅ DEBUGGABILITY: Clear error messages and logging
✅ TYPE SAFETY: Full type hints for IDE support

SOLID Principles Demonstrated:
- S: Each class has one responsibility
- O: Open for extension, closed for modification
- L: Interfaces ensure substitutability
- I: Minimal, focused interfaces
- D: Depend on abstractions (interfaces), not implementations
"""
