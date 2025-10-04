"""
Alerting System - Multi-Channel Notifications

Supports multiple alerting channels with configurable routing.
"""

from .base import (
    Alert,
    AlertLevel,
    BaseAlerter,
    AlertManager,
)

from .email_alerter import EmailAlerter
from .slack_alerter import SlackAlerter


__all__ = [
    # Core
    "Alert",
    "AlertLevel",
    "BaseAlerter",
    "AlertManager",
    # Implementations
    "EmailAlerter",
    "SlackAlerter",
]
