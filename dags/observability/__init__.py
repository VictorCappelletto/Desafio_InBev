"""
Observability Framework - Enterprise Monitoring

Provides comprehensive monitoring, metrics collection, and alerting for data pipelines.

Components:
- Metrics: Collect and track pipeline metrics
- Alerts: Send notifications on failures
- Dashboard: Export metrics for visualization

Features:
- Real-time metrics collection
- Automated alerting (Email/Slack)
- Performance tracking
- Data quality monitoring
- Historical trending

Usage:
    from observability import MetricsCollector, EmailAlerter

    # Collect metrics
    collector = MetricsCollector()
    collector.record_pipeline_metric("brewery_etl", {
        "records_processed": 1000,
        "duration_seconds": 45.2,
        "quality_score": 0.98
    })

    # Send alerts
    alerter = EmailAlerter()
    if quality_score < 0.95:
        alerter.send_alert("Low quality score detected")

See Also:
    - metrics.py: Metrics collection
    - alerts/: Alerting implementations
"""

from .alerts import AlertLevel, BaseAlerter, EmailAlerter, SlackAlerter
from .metrics import (
    DataQualityMetrics,
    MetricsCollector,
    PerformanceMetrics,
    PipelineMetrics,
)

__all__ = [
    # Metrics
    "MetricsCollector",
    "PipelineMetrics",
    "DataQualityMetrics",
    "PerformanceMetrics",
    # Alerts
    "BaseAlerter",
    "EmailAlerter",
    "SlackAlerter",
    "AlertLevel",
]


__version__ = "1.0.0"
