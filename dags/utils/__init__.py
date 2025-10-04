"""
Utils Module

Utility functions and helpers for Airflow DAGs.

This module provides common utilities used across DAGs:
- Logging: Structured logging with consistent formatting
- (Future) Date/Time utilities
- (Future) Data validation helpers
- (Future) Retry decorators

Usage:
    from utils import get_logger, log_task_start, log_task_success

    logger = get_logger(__name__)
    log_task_start(logger, "my_task", source="API")
    # ... task logic ...
    log_task_success(logger, "my_task", records=100)

Available Functions:
- get_logger(): Get configured logger for DAGs
- log_task_start(): Log task start with context
- log_task_success(): Log task completion with metrics
- log_task_error(): Log task error with exception details

See Also:
- logger.py: Logging configuration and helpers
- README.md: Detailed documentation
"""

from .logger import (
    get_logger,
    log_task_error,
    log_task_start,
    log_task_success,
)

__all__ = [
    "get_logger",
    "log_task_start",
    "log_task_success",
    "log_task_error",
]
