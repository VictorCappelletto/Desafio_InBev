# Observability Framework

Sistema completo de **métricas, detecção de anomalias e alertas** para pipelines de dados.

---

## 🎯 Quick Start

### Metrics Collection

```python
from observability import MetricsCollector

collector = MetricsCollector()
metrics = collector.collect_data_metrics(
    data=brewery_data,
    source="Open Brewery API",
    stage="extraction"
)

print(f"Volume: {metrics.volume} records")
print(f"Quality Score: {metrics.quality_score:.2%}")
```

### Alerting

```python
from observability import AlertManager, EmailAlerter
from config import AirflowConfig

# Setup alerting
alert_manager = AlertManager()
alert_manager.add_alerter(EmailAlerter(AirflowConfig()))

# Send alert
alert_manager.send_alerts(
    subject="Pipeline Failed!",
    message="Brewery ETL failed at extraction stage",
    level="critical",
    details={"error": "Connection timeout"}
)
```

---

## 📊 Key Components

### 1. DataMetrics

Tracks pipeline health metrics:

```python
@dataclass
class DataMetrics:
    volume: int              # Record count
    freshness: float         # Hours since last update
    quality_score: float     # 0.0 to 1.0
    processing_time: float   # Seconds
    error_rate: float        # 0.0 to 1.0
    schema_compliance: float # 0.0 to 1.0
```

### 2. MetricsCollector (Singleton)

```python
# Singleton pattern - single instance globally
collector = MetricsCollector()
metrics = collector.collect_data_metrics(data, source, stage)
```

### 3. AnomalyDetector

```python
from observability.metrics import AnomalyDetector

detector = AnomalyDetector()
anomalies = detector.detect(metrics)

if anomalies:
    print(f"⚠️ Anomalies detected: {', '.join(anomalies)}")
```

### 4. Alert Channels

| Channel | Class | Config Required |
|---------|-------|----------------|
| **Email** | `EmailAlerter` | SMTP settings in `AirflowConfig` |
| **Slack** | `SlackAlerter` | `SLACK_WEBHOOK_URL` env var |

---

## 🏗️ Architecture

```python
# Core (dags/observability/)
observability/
├── metrics.py           # DataMetrics, MetricsCollector, AnomalyDetector
└── alerts/
    ├── base.py          # Alerter ABC, AlertLevel enum
    ├── email_alerter.py # Email implementation
    └── slack_alerter.py # Slack implementation
```

---

## 🔧 Custom Alerters

```python
from observability.alerts import Alerter, AlertLevel

class CustomAlerter(Alerter):
    def send_alert(self, subject: str, message: str, 
                   level: AlertLevel, details: dict) -> bool:
        try:
            # Your custom alerting logic (PagerDuty, Teams, etc)
            custom_service.send(subject, message)
            return True
        except Exception as e:
            self.logger.error(f"Alert failed: {e}")
            return False

# Use it
alert_manager = AlertManager()
alert_manager.add_alerter(CustomAlerter())
```

---

## 📖 References

- **Code**: `dags/observability/`
- **API Reference**: Use `help(MetricsCollector)` in Python
- **Alert Config**: See `config/settings.py` → `AirflowConfig`

---

## 💡 Tips

!!! tip "Slack Webhooks"
    Create Slack webhook at: https://api.slack.com/messaging/webhooks
    ```bash
    export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    ```

!!! warning "Email Configuration"
    For Gmail, use App Passwords (not account password):
    ```python
    AIRFLOW__EMAIL__EMAIL_BACKEND="airflow.utils.email.send_email_smtp"
    AIRFLOW__SMTP__SMTP_HOST="smtp.gmail.com"
    AIRFLOW__SMTP__SMTP_PORT=587
    AIRFLOW__SMTP__SMTP_USER="your-email@gmail.com"
    AIRFLOW__SMTP__SMTP_PASSWORD="your-app-password"
    ```

!!! success "DAG Integration"
    Use in Airflow tasks:
    ```python
    from observability import MetricsCollector, AlertManager
    
    @task
    def monitor_pipeline(**context):
        collector = MetricsCollector()
        metrics = collector.collect_data_metrics(...)
        
        if metrics.error_rate > 0.05:  # 5% threshold
            AlertManager().send_alerts(
                subject="High Error Rate!",
                message=f"Error rate: {metrics.error_rate:.2%}",
                level="warning"
            )
    ```

---

## 🎯 Alert Levels

| Level | Color | Use When |
|-------|-------|----------|
| `info` | 🔵 Blue | Informational messages |
| `warning` | 🟡 Yellow | Potential issues, not critical |
| `error` | 🟠 Orange | Errors that need attention |
| `critical` | 🔴 Red | System down, immediate action |

