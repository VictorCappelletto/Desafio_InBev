"""
Logger Configuration for Airflow DAGs

This module provides a standardized logging configuration for all DAGs.
It ensures consistent log formatting and proper integration with Airflow's logging system.

Usage in DAGs:
    from utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Processing started")
    logger.error("An error occurred", exc_info=True)
"""

import logging
import os
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger for DAGs.

    Args:
        name: Logger name (usually __name__ of the module)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If not provided, uses LOG_LEVEL env var or defaults to INFO

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Task started")
        >>> logger.debug("Debug information", extra={"task_id": "my_task"})
    """
    # Get logger
    logger = logging.getLogger(name)

    # Set log level
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()

    logger.setLevel(getattr(logging, level, logging.INFO))

    # Prevent duplicate logs (Airflow already has handlers)
    logger.propagate = True

    return logger


def log_task_start(logger: logging.Logger, task_name: str, **kwargs) -> None:
    """
    Log task start with context information.

    Args:
        logger: Logger instance
        task_name: Name of the task
        **kwargs: Additional context to log

    Example:
        >>> logger = get_logger(__name__)
        >>> log_task_start(logger, "extract_data", source="API", records=100)
    """
    context_str = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(f"[START] Task: {task_name} | {context_str}")


def log_task_success(logger: logging.Logger, task_name: str, **kwargs) -> None:
    """
    Log task completion with metrics.

    Args:
        logger: Logger instance
        task_name: Name of the task
        **kwargs: Metrics to log (e.g., records_processed, duration)

    Example:
        >>> logger = get_logger(__name__)
        >>> log_task_success(logger, "load_data", records=1000, duration="5.2s")
    """
    metrics_str = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(f"[SUCCESS] Task: {task_name} | {metrics_str}")


def log_task_error(
    logger: logging.Logger, task_name: str, error: Exception, **kwargs
) -> None:
    """
    Log task error with exception details.

    Args:
        logger: Logger instance
        task_name: Name of the task
        error: Exception that occurred
        **kwargs: Additional context

    Example:
        >>> logger = get_logger(__name__)
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     log_task_error(logger, "risky_task", e, retry=True)
    """
    context_str = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.error(
        f"[ERROR] Task: {task_name} | Error: {str(error)} | {context_str}",
        exc_info=True,
    )


# ==============================================================================
# Example Usage in DAG
# ==============================================================================
if __name__ == "__main__":
    # Example: How to use in your DAG
    logger = get_logger(__name__)

    log_task_start(logger, "example_task", source="API", target="Database")

    try:
        # Your task logic here
        records_processed = 1000
        log_task_success(
            logger, "example_task", records=records_processed, duration="3.5s"
        )
    except Exception as e:
        log_task_error(logger, "example_task", e, retry_count=1)
