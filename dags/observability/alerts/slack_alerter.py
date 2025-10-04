"""
Slack Alerter - Slack Notifications

Sends alerts to Slack channels via webhooks.
"""

import os
from typing import Any, Dict, Optional

import requests

from .base import Alert, AlertLevel, BaseAlerter


class SlackAlerter(BaseAlerter):
    """
    Send alerts to Slack via webhooks.

    Supports rich message formatting with Slack's Block Kit.

    Environment Variables:
        SLACK_WEBHOOK_URL: Slack webhook URL
        SLACK_CHANNEL: Default channel (optional, webhook may have default)
        SLACK_USERNAME: Bot username (default: "Airflow Alerts")

    Setup:
        1. Create Slack incoming webhook: https://api.slack.com/messaging/webhooks
        2. Set SLACK_WEBHOOK_URL environment variable
        3. Configure alerter and start sending alerts

    Example:
        >>> alerter = SlackAlerter(
        ...     webhook_url="https://hooks.slack.com/services/XXX/YYY/ZZZ",
        ...     channel="#data-alerts",
        ...     username="Data Pipeline Bot"
        ... )
        >>>
        >>> alert = Alert(
        ...     title="Pipeline Failed",
        ...     message="ETL pipeline encountered an error",
        ...     level=AlertLevel.ERROR,
        ...     source="brewery_etl"
        ... )
        >>>
        >>> alerter.send_alert(alert)
    """

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        channel: Optional[str] = None,
        username: str = "Airflow Alerts",
        icon_emoji: str = ":robot_face:",
        enabled: bool = True,
        min_level: AlertLevel = AlertLevel.WARNING,
        timeout: int = 10,
    ):
        """
        Initialize Slack alerter.

        Args:
            webhook_url: Slack webhook URL
            channel: Target channel (optional, webhook may have default)
            username: Bot username
            icon_emoji: Bot icon emoji
            enabled: Whether alerter is enabled
            min_level: Minimum alert level to send
            timeout: Request timeout in seconds
        """
        super().__init__(name="slack", enabled=enabled, min_level=min_level)

        # Load from environment if not provided
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")
        self.channel = channel or os.getenv("SLACK_CHANNEL")
        self.username = username or os.getenv("SLACK_USERNAME", "Airflow Alerts")
        self.icon_emoji = icon_emoji
        self.timeout = timeout

        # Validate configuration
        if not self.webhook_url:
            self.logger.warning(
                "No Slack webhook URL configured - Slack alerts disabled"
            )
            self.enabled = False
        elif not self.webhook_url.startswith("https://hooks.slack.com/"):
            self.logger.warning("Invalid Slack webhook URL - Slack alerts disabled")
            self.enabled = False

    def send_alert(self, alert: Alert) -> bool:
        """
        Send alert to Slack.

        Args:
            alert: Alert to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.webhook_url:
            self.logger.error("No Slack webhook URL configured")
            return False

        try:
            # Create Slack message
            payload = self._create_slack_message(alert)

            # Send to Slack
            response = requests.post(
                self.webhook_url, json=payload, timeout=self.timeout
            )

            if response.status_code == 200:
                self.logger.info(f"Slack alert sent: {alert.title}")
                return True
            else:
                self.logger.error(
                    f"Failed to send Slack alert: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {str(e)}", exc_info=True)
            return False

    def _create_slack_message(self, alert: Alert) -> Dict[str, Any]:
        """
        Create Slack message payload with Block Kit formatting.

        Args:
            alert: Alert to format

        Returns:
            Slack message payload
        """
        # Color mapping for alert levels
        colors = {
            AlertLevel.INFO: "#36a64f",  # Green
            AlertLevel.WARNING: "#ff9900",  # Orange
            AlertLevel.ERROR: "#d00000",  # Red
            AlertLevel.CRITICAL: "#660000",  # Dark red
        }
        color = colors.get(alert.level, "#808080")

        # Build message
        payload = {
            "username": self.username,
            "icon_emoji": self.icon_emoji,
        }

        if self.channel:
            payload["channel"] = self.channel

        # Rich message with blocks
        blocks = []

        # Header
        blocks.append(
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{alert.get_emoji()} {alert.title}",
                    "emoji": True,
                },
            }
        )

        # Message body
        blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": alert.message}}
        )

        # Metadata fields
        fields = [
            {"type": "mrkdwn", "text": f"*Level:*\n{alert.level.value.upper()}"},
            {"type": "mrkdwn", "text": f"*Source:*\n{alert.source}"},
            {
                "type": "mrkdwn",
                "text": f"*Time:*\n{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            },
        ]

        if alert.tags:
            fields.append(
                {"type": "mrkdwn", "text": f"*Tags:*\n{', '.join(alert.tags)}"}
            )

        blocks.append({"type": "section", "fields": fields})

        # Additional metadata
        if alert.metadata:
            metadata_text = ""
            for key, value in alert.metadata.items():
                metadata_text += f"• *{key}:* {value}\n"

            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Additional Details:*\n{metadata_text}",
                    },
                }
            )

        # Divider
        blocks.append({"type": "divider"})

        # Context (footer)
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"Sent by Airflow Observability System"}
                ],
            }
        )

        payload["blocks"] = blocks

        # Fallback text for notifications
        payload["text"] = f"{alert.level.value.upper()}: {alert.title}"

        # Color attachment for mobile/notification
        payload["attachments"] = [{"color": color, "fallback": alert.format_message()}]

        return payload

    def test_connection(self) -> bool:
        """
        Test Slack webhook connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_payload = {
                "username": self.username,
                "icon_emoji": self.icon_emoji,
                "text": "[OK] Slack alerter test - Connection successful!",
            }

            if self.channel:
                test_payload["channel"] = self.channel

            response = requests.post(
                self.webhook_url, json=test_payload, timeout=self.timeout
            )

            if response.status_code == 200:
                self.logger.info("Slack connection test successful")
                return True
            else:
                self.logger.error(
                    f"Slack connection test failed: {response.status_code}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Slack connection test failed: {str(e)}")
            return False

    def send_simple(self, message: str, emoji: str = ":information_source:") -> bool:
        """
        Send simple text message (without alert formatting).

        Args:
            message: Message text
            emoji: Emoji to display

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.webhook_url:
            return False

        try:
            payload = {
                "username": self.username,
                "icon_emoji": self.icon_emoji,
                "text": f"{emoji} {message}",
            }

            if self.channel:
                payload["channel"] = self.channel

            response = requests.post(
                self.webhook_url, json=payload, timeout=self.timeout
            )

            return response.status_code == 200

        except Exception as e:
            self.logger.error(f"Failed to send simple Slack message: {str(e)}")
            return False
