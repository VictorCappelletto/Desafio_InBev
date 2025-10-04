"""
Base Alerting System - Enterprise Notifications

Abstract base for alerting implementations.
Supports multiple alert levels and channels.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AlertLevel(Enum):
    """
    Alert severity levels.

    Used to prioritize and route alerts appropriately.
    """

    INFO = "info"  # Informational only
    WARNING = "warning"  # Potential issue
    ERROR = "error"  # Confirmed issue
    CRITICAL = "critical"  # Severe issue requiring immediate attention


@dataclass
class Alert:
    """
    Alert message with metadata.

    Represents a single alert to be sent through alerting channels.

    Attributes:
        title: Alert title/subject
        message: Detailed alert message
        level: Alert severity level
        source: Source of the alert (e.g., pipeline name)
        timestamp: When alert was created
        metadata: Additional context
        tags: Tags for categorization
    """

    title: str
    message: str
    level: AlertLevel
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "title": self.title,
            "message": self.message,
            "level": self.level.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "tags": self.tags,
        }

    def get_emoji(self) -> str:
        """Get emoji for alert level."""
        emoji_map = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨",
        }
        return emoji_map.get(self.level, "📢")

    def format_message(self) -> str:
        """
        Format alert as human-readable text.

        Returns:
            Formatted alert message
        """
        lines = [
            f"{self.get_emoji()} {self.level.value.upper()}: {self.title}",
            "",
            self.message,
            "",
            f"Source: {self.source}",
            f"Time: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        if self.tags:
            lines.append(f"Tags: {', '.join(self.tags)}")

        if self.metadata:
            lines.append("")
            lines.append("Additional Details:")
            for key, value in self.metadata.items():
                lines.append(f"  • {key}: {value}")

        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Alert(level={self.level.value}, title='{self.title}', source='{self.source}')"


class BaseAlerter(ABC):
    """
    Abstract base class for alert implementations.

    All alerting channels must inherit from this class and implement
    the send_alert method.

    Example:
        class CustomAlerter(BaseAlerter):
            def __init__(self):
                super().__init__(name="custom")

            def send_alert(self, alert: Alert) -> bool:
                # Custom implementation
                print(f"Sending to custom channel: {alert.title}")
                return True
    """

    def __init__(
        self,
        name: str,
        enabled: bool = True,
        min_level: AlertLevel = AlertLevel.WARNING,
    ):
        """
        Initialize alerter.

        Args:
            name: Alerter name/identifier
            enabled: Whether alerter is enabled
            min_level: Minimum alert level to send
        """
        self.name = name
        self.enabled = enabled
        self.min_level = min_level
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self._sent_count = 0
        self._failed_count = 0

    @abstractmethod
    def send_alert(self, alert: Alert) -> bool:
        """
        Send alert through this channel.

        Args:
            alert: Alert to send

        Returns:
            True if sent successfully, False otherwise

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        pass

    def should_send(self, alert: Alert) -> bool:
        """
        Check if alert should be sent based on configuration.

        Args:
            alert: Alert to check

        Returns:
            True if alert should be sent, False otherwise
        """
        if not self.enabled:
            self.logger.debug(f"Alerter {self.name} is disabled")
            return False

        # Check minimum level
        level_order = {
            AlertLevel.INFO: 0,
            AlertLevel.WARNING: 1,
            AlertLevel.ERROR: 2,
            AlertLevel.CRITICAL: 3,
        }

        if level_order[alert.level] < level_order[self.min_level]:
            self.logger.debug(
                f"Alert level {alert.level.value} below minimum {self.min_level.value}"
            )
            return False

        return True

    def try_send(self, alert: Alert) -> bool:
        """
        Try to send alert with error handling.

        Args:
            alert: Alert to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.should_send(alert):
            return False

        try:
            self.logger.info(
                f"Sending {alert.level.value} alert: {alert.title}",
                extra={"alert_title": alert.title, "level": alert.level.value},
            )

            success = self.send_alert(alert)

            if success:
                self._sent_count += 1
                self.logger.info(f"Alert sent successfully via {self.name}")
            else:
                self._failed_count += 1
                self.logger.error(f"Failed to send alert via {self.name}")

            return success

        except Exception as e:
            self._failed_count += 1
            self.logger.error(
                f"Error sending alert via {self.name}: {str(e)}", exc_info=True
            )
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get alerter statistics.

        Returns:
            Dictionary with sent/failed counts
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "min_level": self.min_level.value,
            "sent_count": self._sent_count,
            "failed_count": self._failed_count,
            "success_rate": (
                self._sent_count / (self._sent_count + self._failed_count)
                if (self._sent_count + self._failed_count) > 0
                else 0.0
            ),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', enabled={self.enabled})"


class AlertManager:
    """
    Manages multiple alerters and routes alerts to appropriate channels.

    Example:
        >>> manager = AlertManager()
        >>> manager.add_alerter(EmailAlerter())
        >>> manager.add_alerter(SlackAlerter())
        >>>
        >>> # Send to all channels
        >>> manager.send(Alert(
        ...     title="Pipeline Failed",
        ...     message="ETL pipeline failed after 100 records",
        ...     level=AlertLevel.ERROR,
        ...     source="brewery_etl"
        ... ))
    """

    def __init__(self):
        """Initialize alert manager."""
        self.alerters: List[BaseAlerter] = []
        self.logger = logging.getLogger(__name__)

    def add_alerter(self, alerter: BaseAlerter) -> "AlertManager":
        """
        Add an alerter to the manager.

        Args:
            alerter: Alerter to add

        Returns:
            Self for method chaining
        """
        self.alerters.append(alerter)
        self.logger.info(f"Added alerter: {alerter.name}")
        return self

    def remove_alerter(self, name: str) -> bool:
        """
        Remove an alerter by name.

        Args:
            name: Name of alerter to remove

        Returns:
            True if removed, False if not found
        """
        for i, alerter in enumerate(self.alerters):
            if alerter.name == name:
                self.alerters.pop(i)
                self.logger.info(f"Removed alerter: {name}")
                return True
        return False

    def send(self, alert: Alert) -> Dict[str, bool]:
        """
        Send alert to all registered alerters.

        Args:
            alert: Alert to send

        Returns:
            Dict mapping alerter names to success status
        """
        if not self.alerters:
            self.logger.warning("No alerters registered")
            return {}

        results = {}
        for alerter in self.alerters:
            success = alerter.try_send(alert)
            results[alerter.name] = success

        return results

    def send_quick(
        self,
        title: str,
        message: str,
        level: AlertLevel = AlertLevel.WARNING,
        source: str = "unknown",
        **metadata,
    ) -> Dict[str, bool]:
        """
        Quick send - Create and send alert in one call.

        Args:
            title: Alert title
            message: Alert message
            level: Alert level
            source: Alert source
            **metadata: Additional metadata as kwargs

        Returns:
            Dict mapping alerter names to success status
        """
        alert = Alert(
            title=title, message=message, level=level, source=source, metadata=metadata
        )
        return self.send(alert)

    def get_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all alerters."""
        return [alerter.get_stats() for alerter in self.alerters]

    def __repr__(self) -> str:
        return f"AlertManager(alerters={len(self.alerters)})"
