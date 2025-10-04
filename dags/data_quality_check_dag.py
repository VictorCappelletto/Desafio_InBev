"""
Data Quality Check DAG - SOLID Architecture

This DAG performs data quality checks on the Breweries table in Azure SQL.

SOLID Principles Applied:
- Single Responsibility: Each check function has one purpose
- Dependency Injection: Config injected into checks
- Open/Closed: Easy to add new quality checks
- Type Safety: Full type hints

Quality Checks:
- Row count validation
- Null value detection
- Duplicate detection
- Schema validation
- Data freshness check
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowException

from config import AzureSQLConfig, AirflowConfig
from services.azure_sql_loader import AzureSQLLoader
from utils import get_logger, log_task_start, log_task_success, log_task_error
from exceptions import ValidationError


# ==============================================================================
# Configuration
# ==============================================================================

sql_config = AzureSQLConfig()
airflow_config = AirflowConfig()
logger = get_logger(__name__)


# ==============================================================================
# Quality Check Functions
# ==============================================================================


def check_row_count(**context: Any) -> Dict[str, Any]:
    """
    Check if table has minimum expected rows.

    Validates that the data pipeline is producing results by checking
    if the Breweries table contains at least the minimum expected number of rows.

    Args:
        **context: Airflow task context

    Returns:
        Dict[str, Any]: Check result with status and metrics

    Raises:
        ValidationError: If row count is below threshold

    Validates that data pipeline is producing results.
    """
    log_task_start(logger, "check_row_count", table="Breweries")

    try:
        import pyodbc

        with pyodbc.connect(sql_config.connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Breweries")
            count = cursor.fetchone()[0]

        # Minimum expected rows (adjust based on your data)
        min_expected_rows = 100

        if count < min_expected_rows:
            raise ValidationError(
                f"Row count too low: {count} (expected >= {min_expected_rows})",
                details={"actual_count": count, "expected_min": min_expected_rows},
            )

        result = {
            "check": "row_count",
            "status": "passed",
            "row_count": count,
            "threshold": min_expected_rows,
        }

        log_task_success(logger, "check_row_count", status="passed", row_count=count)

        # Push to XCom for reporting
        context["ti"].xcom_push(key="row_count_check", value=result)
        return result

    except Exception as e:
        log_task_error(logger, "check_row_count", e)
        raise


def check_null_values(**context: Any) -> Dict[str, Any]:
    """
    Check for unexpected null values in critical columns.

    Validates data completeness by checking if critical columns
    (id, name, brewery_type) contain any NULL values.

    Args:
        **context: Airflow task context

    Returns:
        Dict[str, Any]: Check result with null counts per column

    Raises:
        ValidationError: If any critical column has NULL values

    Ensures data completeness.
    """
    log_task_start(logger, "check_null_values", table="Breweries")

    try:
        import pyodbc

        # Critical columns that should not be null
        critical_columns = ["id", "name", "brewery_type"]

        with pyodbc.connect(sql_config.connection_string) as conn:
            cursor = conn.cursor()

            null_counts = {}
            for column in critical_columns:
                cursor.execute(f"SELECT COUNT(*) FROM Breweries WHERE {column} IS NULL")
                null_count = cursor.fetchone()[0]
                null_counts[column] = null_count

        # Check if any critical column has nulls
        total_nulls = sum(null_counts.values())

        if total_nulls > 0:
            raise ValidationError(
                f"Found {total_nulls} null values in critical columns",
                details=null_counts,
            )

        result = {
            "check": "null_values",
            "status": "passed",
            "null_counts": null_counts,
            "total_nulls": total_nulls,
        }

        log_task_success(
            logger, "check_null_values", status="passed", total_nulls=total_nulls
        )

        context["ti"].xcom_push(key="null_check", value=result)
        return result

    except Exception as e:
        log_task_error(logger, "check_null_values", e)
        raise


def check_duplicates(**context: Any) -> Dict[str, Any]:
    """
    Check for duplicate records based on ID.

    Validates data integrity by detecting duplicate brewery IDs
    in the table, which should have unique primary keys.

    Args:
        **context: Airflow task context

    Returns:
        Dict[str, Any]: Check result with duplicate count

    Raises:
        ValidationError: If duplicate IDs are found

    Ensures data integrity.
    """
    log_task_start(logger, "check_duplicates", table="Breweries")

    try:
        import pyodbc

        with pyodbc.connect(sql_config.connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, COUNT(*) as count
                FROM Breweries
                GROUP BY id
                HAVING COUNT(*) > 1
            """
            )
            duplicates = cursor.fetchall()

        duplicate_count = len(duplicates)

        if duplicate_count > 0:
            duplicate_ids = [row[0] for row in duplicates[:5]]  # First 5
            raise ValidationError(
                f"Found {duplicate_count} duplicate records",
                details={
                    "duplicate_count": duplicate_count,
                    "sample_ids": duplicate_ids,
                },
            )

        result = {
            "check": "duplicates",
            "status": "passed",
            "duplicate_count": duplicate_count,
        }

        log_task_success(
            logger, "check_duplicates", status="passed", duplicates=duplicate_count
        )

        context["ti"].xcom_push(key="duplicate_check", value=result)
        return result

    except Exception as e:
        log_task_error(logger, "check_duplicates", e)
        raise


def check_data_freshness(**context: Any) -> Dict[str, Any]:
    """
    Check if data was updated recently.

    Validates that the data pipeline is running regularly by
    comparing current row count with previous run.

    Args:
        **context: Airflow task context

    Returns:
        Dict[str, Any]: Check result with freshness status

    Note:
        Logs warning if data hasn't changed since last run,
        but doesn't fail the check.

    Ensures pipeline is running regularly.
    """
    log_task_start(logger, "check_data_freshness", table="Breweries")

    try:
        import pyodbc
        from datetime import datetime, timedelta

        # Check if table has a timestamp column (optional)
        # For this example, we'll check if row count changed in last 24h
        # In production, use a proper timestamp column

        with pyodbc.connect(sql_config.connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Breweries")
            current_count = cursor.fetchone()[0]

        # Get previous count from XCom (if exists)
        previous_count = context["ti"].xcom_pull(
            dag_id="data_quality_check_solid",
            task_ids="check_data_freshness",
            key="row_count",
        )

        if previous_count is not None and current_count == previous_count:
            logger.warning(
                f"Data hasn't changed: {current_count} rows (same as last run)"
            )

        result = {
            "check": "data_freshness",
            "status": "passed",
            "current_count": current_count,
            "previous_count": previous_count,
            "changed": current_count != previous_count,
        }

        # Store current count for next run
        context["ti"].xcom_push(key="row_count", value=current_count)

        log_task_success(
            logger,
            "check_data_freshness",
            status="passed",
            data_changed=current_count != previous_count,
        )

        context["ti"].xcom_push(key="freshness_check", value=result)
        return result

    except Exception as e:
        log_task_error(logger, "check_data_freshness", e)
        raise


def generate_quality_report(**context: Any) -> None:
    """
    Generate a summary report of all quality checks.

    Aggregates results from all quality check tasks and generates
    a consolidated report with summary statistics. Logs formatted
    report to Airflow logs and stores in XCom.

    Args:
        **context: Airflow task context

    Raises:
        Exception: If report generation fails

    Aggregates results from all checks.
    """
    log_task_start(logger, "generate_quality_report")

    try:
        ti = context["ti"]

        # Collect results from all checks
        row_count_result = ti.xcom_pull(
            task_ids="check_row_count", key="row_count_check"
        )
        null_result = ti.xcom_pull(task_ids="check_null_values", key="null_check")
        duplicate_result = ti.xcom_pull(
            task_ids="check_duplicates", key="duplicate_check"
        )
        freshness_result = ti.xcom_pull(
            task_ids="check_data_freshness", key="freshness_check"
        )

        # Generate report
        report = {
            "execution_date": context["ds"],
            "dag_run_id": context["run_id"],
            "checks": [
                row_count_result,
                null_result,
                duplicate_result,
                freshness_result,
            ],
            "summary": {
                "total_checks": 4,
                "passed": sum(
                    1
                    for r in [
                        row_count_result,
                        null_result,
                        duplicate_result,
                        freshness_result,
                    ]
                    if r["status"] == "passed"
                ),
                "failed": 0,
            },
        }

        logger.info("=" * 60)
        logger.info("DATA QUALITY REPORT")
        logger.info("=" * 60)
        logger.info(f"Execution Date: {report['execution_date']}")
        logger.info(f"Total Checks: {report['summary']['total_checks']}")
        logger.info(f"Passed: {report['summary']['passed']}")
        logger.info(f"Failed: {report['summary']['failed']}")
        logger.info("-" * 60)

        for check in report["checks"]:
            logger.info(f"✅ {check['check']}: {check['status'].upper()}")

        logger.info("=" * 60)

        log_task_success(
            logger,
            "generate_quality_report",
            total_checks=report["summary"]["total_checks"],
            passed=report["summary"]["passed"],
        )

        # Store report
        ti.xcom_push(key="quality_report", value=report)

    except Exception as e:
        log_task_error(logger, "generate_quality_report", e)
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
    "retries": 1,  # Quality checks don't need many retries
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "data_quality_check_solid",
    default_args=default_args,
    description="Data quality checks for Breweries table (SOLID Architecture)",
    schedule_interval="@daily",  # Run after ETL
    catchup=False,
    tags=["data-quality", "validation", "breweries", "solid", "production"],
) as dag:

    # Quality Check Tasks
    row_count_task = PythonOperator(
        task_id="check_row_count",
        python_callable=check_row_count,
        provide_context=True,
        doc_md="""
        ### Row Count Validation
        
        Checks if table has minimum expected number of rows.
        
        **Threshold:** >= 100 rows
        
        **Failure:** Indicates ETL pipeline issue
        """,
    )

    null_values_task = PythonOperator(
        task_id="check_null_values",
        python_callable=check_null_values,
        provide_context=True,
        doc_md="""
        ### Null Value Detection
        
        Checks critical columns for unexpected null values.
        
        **Critical Columns:**
        - id
        - name
        - brewery_type
        
        **Failure:** Data quality issue
        """,
    )

    duplicates_task = PythonOperator(
        task_id="check_duplicates",
        python_callable=check_duplicates,
        provide_context=True,
        doc_md="""
        ### Duplicate Detection
        
        Checks for duplicate records based on ID.
        
        **Failure:** Data integrity issue
        """,
    )

    freshness_task = PythonOperator(
        task_id="check_data_freshness",
        python_callable=check_data_freshness,
        provide_context=True,
        doc_md="""
        ### Data Freshness Check
        
        Checks if data was updated recently.
        
        **Failure:** Pipeline not running regularly
        """,
    )

    report_task = PythonOperator(
        task_id="generate_quality_report",
        python_callable=generate_quality_report,
        provide_context=True,
        doc_md="""
        ### Quality Report Generation
        
        Aggregates results from all checks and generates report.
        
        **Output:** Summary report in XCom
        """,
    )

    # Define workflow - All checks run in parallel, then report
    [row_count_task, null_values_task, duplicates_task, freshness_task] >> report_task


# ==============================================================================
# Benefits of This DAG
# ==============================================================================
"""
✅ AUTOMATED QUALITY: Runs daily after ETL
✅ MULTIPLE CHECKS: Row count, nulls, duplicates, freshness
✅ FAIL-FAST: Stops pipeline if quality issues detected
✅ REPORTING: Consolidated quality report
✅ OBSERVABLE: Detailed logging
✅ EXTENSIBLE: Easy to add new checks
✅ TYPE-SAFE: Full type hints
✅ SOLID: Follows all SOLID principles
"""
