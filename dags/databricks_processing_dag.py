"""
Databricks Processing DAG - SOLID Architecture

Executes Databricks notebook for data processing (Silver layer).

SOLID Principles Applied:
- Configuration via dataclasses
- Type safety with full type hints
- Professional error handling
- Structured logging
"""

from datetime import datetime, timedelta
from typing import Any

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from config import AirflowConfig, DatabricksConfig
from utils import get_logger, log_task_error, log_task_start, log_task_success

# ==============================================================================
# Configuration
# ==============================================================================

databricks_config = DatabricksConfig()
airflow_config = AirflowConfig()
logger = get_logger(__name__)


# ==============================================================================
# Helper Functions
# ==============================================================================


def validate_databricks_config(**context: Any) -> None:
    """
    Validate Databricks configuration before execution.

    Ensures all required Databricks configurations are set and valid
    before attempting to run expensive operations on Databricks cluster.
    Implements fail-fast principle to catch configuration errors early.

    Args:
        **context: Airflow task context

    Raises:
        ValueError: If any required configuration is missing or contains placeholder values

    Demonstrates:
    - Fail-fast principle
    - Configuration validation
    - Clear error messages
    - Professional error handling
    """
    log_task_start(
        logger,
        "validate_databricks_config",
        host=databricks_config.host,
        cluster_id=databricks_config.cluster_id,
    )

    try:
        config_checks = {
            "host": databricks_config.host,
            "cluster_id": databricks_config.cluster_id,
            "job_id": databricks_config.job_id,
            "notebook_path": databricks_config.notebook_path,
        }

        # Collect all missing/invalid configurations
        invalid_configs = []
        for key, value in config_checks.items():
            if "XXX" in str(value) or "example.com" in str(value) or not value:
                invalid_configs.append(key)

        # Fail with comprehensive error message
        if invalid_configs:
            error_msg = (
                f"Databricks configuration incomplete: {', '.join(invalid_configs)}. "
                f"Please configure these in .env file"
            )
            raise ValueError(error_msg)

        logger.info(f"✅ Databricks configuration validated: {databricks_config}")
        log_task_success(
            logger,
            "validate_databricks_config",
            config_valid=True,
            checks_passed=len(config_checks),
            host=databricks_config.host,
        )

    except Exception as e:
        log_task_error(logger, "validate_databricks_config", e)
        raise


# ==============================================================================
# DAG Definition
# ==============================================================================

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 10, 1),
    "email_on_failure": airflow_config.email_on_failure,
    "email_on_retry": airflow_config.email_on_retry,
    "retries": airflow_config.default_retries,
    "retry_delay": timedelta(seconds=airflow_config.retry_delay_seconds),
}

with DAG(
    "databricks_processing_solid",
    default_args=default_args,
    description="Execute Databricks notebook for data processing (SOLID Architecture)",
    schedule_interval="@daily",
    catchup=False,
    tags=["databricks", "processing", "silver-layer", "solid", "production"],
) as dag:

    # Task 1: Validate Configuration
    validate_config_task = PythonOperator(
        task_id="validate_config",
        python_callable=validate_databricks_config,
        provide_context=True,
        doc_md="""
        ### Validate Databricks Configuration
        
        Ensures all required Databricks configurations are set.
        Fails fast if any configuration is missing or invalid.
        
        **Checks:**
        - Databricks host URL
        - Cluster ID
        - Job ID
        - Notebook path
        """,
    )

    # Task 2: Run Databricks Notebook
    run_notebook_task = DatabricksRunNowOperator(
        task_id="run_databricks_notebook",
        databricks_conn_id=databricks_config.connection_id,
        job_id=databricks_config.job_id,
        notebook_params={
            "environment": airflow_config.environment,
            "log_level": airflow_config.log_level,
            "execution_date": "{{ ds }}",
            "dag_run_id": "{{ run_id }}",
        },
        doc_md="""
        ### Execute Databricks Notebook
        
        Runs the data processing notebook on Databricks.
        
        **Configuration:**
        - Connection: `databricks_default` (from airflow_settings.yaml)
        - Job ID: From `DATABRICKS_JOB_ID` environment variable
        - Cluster: From `DATABRICKS_CLUSTER_ID` environment variable
        
        **Parameters Passed:**
        - environment: Current environment (dev/staging/prod)
        - log_level: Logging level
        - execution_date: DAG execution date
        - dag_run_id: Unique run identifier
        """,
    )

    # Define workflow
    validate_config_task >> run_notebook_task


# ==============================================================================
# Architecture Benefits
# ==============================================================================
"""
✅ CONFIGURATION: All settings via environment variables
✅ TYPE SAFETY: Full type hints with dataclasses
✅ FAIL-FAST: Validates config before expensive operations
✅ OBSERVABILITY: Passes execution context to Databricks
✅ REUSABILITY: Config classes can be reused
✅ TESTABILITY: Easy to mock configurations
✅ DOCUMENTATION: Clear docstrings and inline docs
"""
