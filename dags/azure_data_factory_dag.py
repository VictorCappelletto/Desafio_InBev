"""
Azure Data Factory DAG - SOLID Architecture

Triggers Azure Data Factory pipeline execution.

SOLID Principles Applied:
- Configuration via dataclasses
- Type safety
- Professional error handling
- Structured logging
"""

from datetime import datetime, timedelta

from typing import Any

from airflow import DAG
from airflow.providers.microsoft.azure.operators.data_factory import (
    AzureDataFactoryRunPipelineOperator
)
from airflow.operators.python import PythonOperator

from config import AzureDataFactoryConfig, AirflowConfig
from utils import get_logger, log_task_start, log_task_success, log_task_error


# ==============================================================================
# Configuration
# ==============================================================================

adf_config = AzureDataFactoryConfig()
airflow_config = AirflowConfig()
logger = get_logger(__name__)


# ==============================================================================
# Helper Functions
# ==============================================================================

def validate_adf_config(**context: Any) -> None:
    """
    Validate Azure Data Factory configuration.
    
    Performs comprehensive validation of all ADF settings before pipeline execution.
    Uses fail-fast approach to catch configuration issues early.
    
    Args:
        **context: Airflow task context
    
    Raises:
        ValueError: If any configuration is missing or contains placeholder values
    
    Demonstrates:
    - Fail-fast validation
    - Clear error messages
    - Configuration checking
    - Structured logging
    """
    log_task_start(
        logger, 
        "validate_adf_config",
        factory=adf_config.factory_name
    )
    
    try:
        config_checks = {
            'resource_group': adf_config.resource_group,
            'factory_name': adf_config.factory_name,
            'pipeline_name': adf_config.pipeline_name,
            'tenant_id': adf_config.tenant_id,
            'subscription_id': adf_config.subscription_id,
        }
        
        # Check for placeholder values
        missing_configs = []
        for key, value in config_checks.items():
            if 'xxx' in str(value).lower() or not value:
                missing_configs.append(key)
        
        if missing_configs:
            error_msg = (
                f"ADF configuration incomplete: {', '.join(missing_configs)}. "
                f"Please configure these in .env file"
            )
            raise ValueError(error_msg)
        
        logger.info(f"✅ ADF configuration validated: {adf_config}")
        log_task_success(
            logger, 
            "validate_adf_config",
            config_valid=True,
            checks_passed=len(config_checks)
        )
        
    except Exception as e:
        log_task_error(logger, "validate_adf_config", e)
        raise


def log_pipeline_parameters(**context: Any) -> None:
    """
    Log parameters that will be sent to ADF pipeline.
    
    Logs all execution parameters for comprehensive audit trail and debugging.
    Helps track pipeline executions and troubleshoot issues.
    
    Args:
        **context: Airflow task context
    
    Demonstrates:
    - Audit logging
    - Parameter visibility
    - Execution tracking
    """
    log_task_start(logger, "log_parameters")
    
    try:
        logger.info("📋 Pipeline execution parameters:")
        logger.info(f"  🏢 Resource Group: {adf_config.resource_group}")
        logger.info(f"  🏭 Factory: {adf_config.factory_name}")
        logger.info(f"  ⚙️  Pipeline: {adf_config.pipeline_name}")
        logger.info(f"  🌍 Environment: {airflow_config.environment}")
        logger.info(f"  📅 Execution Date: {context['ds']}")
        logger.info(f"  🆔 DAG Run ID: {context.get('run_id', 'N/A')}")
        logger.info(f"  🔗 Connection: {adf_config.connection_id}")
        
        log_task_success(
            logger,
            "log_parameters",
            factory=adf_config.factory_name,
            pipeline=adf_config.pipeline_name
        )
        
    except Exception as e:
        log_task_error(logger, "log_parameters", e)
        raise


# ==============================================================================
# DAG Definition
# ==============================================================================

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 1),
    'email_on_failure': airflow_config.email_on_failure,
    'email_on_retry': airflow_config.email_on_retry,
    'retries': airflow_config.default_retries,
    'retry_delay': timedelta(seconds=airflow_config.retry_delay_seconds),
}

with DAG(
    'azure_data_factory_solid',
    default_args=default_args,
    description='Trigger Azure Data Factory pipeline (SOLID Architecture)',
    schedule_interval='@daily',
    catchup=False,
    tags=['azure', 'data-factory', 'pipeline', 'solid', 'production'],
) as dag:
    
    # Task 1: Validate Configuration
    validate_config_task = PythonOperator(
        task_id='validate_config',
        python_callable=validate_adf_config,
        provide_context=True,
        doc_md="""
        ### Validate ADF Configuration
        
        Validates all required Azure Data Factory settings.
        
        **Checks:**
        - Resource group name
        - Factory name
        - Pipeline name
        - Tenant ID
        - Subscription ID
        """,
    )
    
    # Task 2: Log Parameters
    log_params_task = PythonOperator(
        task_id='log_parameters',
        python_callable=log_pipeline_parameters,
        provide_context=True,
        doc_md="""
        ### Log Pipeline Parameters
        
        Logs all parameters for audit trail.
        Helps with debugging and tracking pipeline executions.
        """,
    )
    
    # Task 3: Trigger ADF Pipeline
    trigger_pipeline_task = AzureDataFactoryRunPipelineOperator(
        task_id='run_adf_pipeline',
        pipeline_name=adf_config.pipeline_name,
        resource_group_name=adf_config.resource_group,
        factory_name=adf_config.factory_name,
        azure_data_factory_conn_id=adf_config.connection_id,
        parameters={
            'environment': airflow_config.environment,
            'execution_date': '{{ ds }}',
            'dag_run_id': '{{ run_id }}',
        },
        doc_md="""
        ### Trigger Azure Data Factory Pipeline
        
        Executes the configured ADF pipeline.
        
        **Configuration:**
        - Connection: `azure_data_factory_default`
        - Resource Group: From `ADF_RESOURCE_GROUP` env var
        - Factory: From `ADF_FACTORY_NAME` env var
        - Pipeline: From `ADF_PIPELINE_NAME` env var
        
        **Parameters Passed:**
        - environment: Current environment
        - execution_date: DAG execution date
        - dag_run_id: Unique run identifier
        """,
    )
    
    # Define workflow
    validate_config_task >> log_params_task >> trigger_pipeline_task


# ==============================================================================
# Architecture Benefits
# ==============================================================================
"""
✅ CONFIGURATION: Environment-driven setup
✅ VALIDATION: Fail-fast approach
✅ OBSERVABILITY: Comprehensive logging
✅ TRACEABILITY: Parameters passed to ADF
✅ TYPE SAFETY: Dataclass configurations
✅ MAINTAINABILITY: Clear separation of concerns
✅ DOCUMENTATION: Inline documentation
"""

