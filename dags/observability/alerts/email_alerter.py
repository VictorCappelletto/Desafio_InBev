"""
Email Alerter - Email Notifications

Sends alerts via email using SMTP.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from .base import Alert, AlertLevel, BaseAlerter


class EmailAlerter(BaseAlerter):
    """
    Send alerts via email.

    Supports HTML and plain text emails with configurable SMTP settings.

    Environment Variables:
        SMTP_HOST: SMTP server host (default: localhost)
        SMTP_PORT: SMTP server port (default: 587)
        SMTP_USER: SMTP username
        SMTP_PASSWORD: SMTP password
        SMTP_FROM: From email address
        ALERT_EMAIL_TO: Comma-separated list of recipient emails

    Example:
        >>> alerter = EmailAlerter(
        ...     smtp_host="smtp.gmail.com",
        ...     smtp_port=587,
        ...     smtp_user="alerts@company.com",
        ...     smtp_password="password",
        ...     from_email="alerts@company.com",
        ...     to_emails=["team@company.com"]
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
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        to_emails: Optional[List[str]] = None,
        use_tls: bool = True,
        enabled: bool = True,
        min_level: AlertLevel = AlertLevel.WARNING,
    ):
        """
        Initialize email alerter.

        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: From email address
            to_emails: List of recipient email addresses
            use_tls: Whether to use TLS (default: True)
            enabled: Whether alerter is enabled
            min_level: Minimum alert level to send
        """
        super().__init__(name="email", enabled=enabled, min_level=min_level)

        # Load from environment if not provided
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER", "")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.from_email = from_email or os.getenv("SMTP_FROM", "airflow@company.com")
        self.use_tls = use_tls

        # Parse to_emails
        if to_emails is None:
            email_str = os.getenv("ALERT_EMAIL_TO", "")
            self.to_emails = [e.strip() for e in email_str.split(",") if e.strip()]
        else:
            self.to_emails = to_emails

        # Validate configuration
        if not self.to_emails:
            self.logger.warning(
                "No recipient emails configured - email alerts disabled"
            )
            self.enabled = False

    def send_alert(self, alert: Alert) -> bool:
        """
        Send alert via email.

        Args:
            alert: Alert to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.to_emails:
            self.logger.error("No recipient emails configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{alert.level.value.upper()}] {alert.title}"
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)

            # Plain text version
            text_body = alert.format_message()
            part1 = MIMEText(text_body, "plain")

            # HTML version
            html_body = self._create_html_email(alert)
            part2 = MIMEText(html_body, "html")

            # Attach both versions
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()

                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)

                server.send_message(msg)

            self.logger.info(
                f"Email sent to {len(self.to_emails)} recipients: {alert.title}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            return False

    def _create_html_email(self, alert: Alert) -> str:
        """
        Create HTML email body.

        Args:
            alert: Alert to format

        Returns:
            HTML string
        """
        # Color mapping for alert levels
        colors = {
            AlertLevel.INFO: "#17a2b8",
            AlertLevel.WARNING: "#ffc107",
            AlertLevel.ERROR: "#dc3545",
            AlertLevel.CRITICAL: "#721c24",
        }
        color = colors.get(alert.level, "#6c757d")

        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .alert-container {{
                    max-width: 600px;
                    margin: 20px auto;
                    border: 2px solid {color};
                    border-radius: 5px;
                    overflow: hidden;
                }}
                .alert-header {{
                    background-color: {color};
                    color: white;
                    padding: 20px;
                    font-size: 18px;
                    font-weight: bold;
                }}
                .alert-body {{
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .alert-message {{
                    background-color: white;
                    padding: 15px;
                    border-radius: 3px;
                    margin: 15px 0;
                    white-space: pre-wrap;
                }}
                .alert-meta {{
                    font-size: 12px;
                    color: #6c757d;
                    margin-top: 15px;
                }}
                .alert-meta-item {{
                    margin: 5px 0;
                }}
                .metadata-table {{
                    width: 100%;
                    margin-top: 15px;
                    border-collapse: collapse;
                }}
                .metadata-table td {{
                    padding: 8px;
                    border-bottom: 1px solid #dee2e6;
                }}
                .metadata-table td:first-child {{
                    font-weight: bold;
                    width: 30%;
                }}
            </style>
        </head>
        <body>
            <div class="alert-container">
                <div class="alert-header">
                    {alert.get_emoji()} {alert.level.value.upper()}: {alert.title}
                </div>
                <div class="alert-body">
                    <div class="alert-message">
                        {alert.message.replace(chr(10), '<br>')}
                    </div>
                    
                    <div class="alert-meta">
                        <div class="alert-meta-item"><strong>Source:</strong> {alert.source}</div>
                        <div class="alert-meta-item"><strong>Time:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
        """

        if alert.tags:
            html += f"""
                        <div class="alert-meta-item"><strong>Tags:</strong> {', '.join(alert.tags)}</div>
        """

        if alert.metadata:
            html += """
                        <table class="metadata-table">
                            <tr><td colspan="2"><strong>Additional Details:</strong></td></tr>
        """
            for key, value in alert.metadata.items():
                html += f"""
                            <tr>
                                <td>{key}</td>
                                <td>{value}</td>
                            </tr>
        """
            html += """
                        </table>
        """

        html += """
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def test_connection(self) -> bool:
        """
        Test SMTP connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)

            self.logger.info("SMTP connection test successful")
            return True

        except Exception as e:
            self.logger.error(f"SMTP connection test failed: {str(e)}")
            return False
