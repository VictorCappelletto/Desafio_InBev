"""
Metrics Collection - Enterprise Observability

Collects, tracks, and exports metrics for data pipelines.
Supports multiple metric types and export formats.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import logging


class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"       # Incrementing value (e.g., records processed)
    GAUGE = "gauge"           # Point-in-time value (e.g., quality score)
    HISTOGRAM = "histogram"   # Distribution (e.g., processing times)
    TIMER = "timer"           # Duration measurement


@dataclass
class PipelineMetrics:
    """
    Metrics for a complete pipeline execution.
    
    Tracks key performance indicators for data pipeline runs.
    
    Attributes:
        pipeline_name: Name of the pipeline
        execution_id: Unique execution identifier
        started_at: Start timestamp
        completed_at: Completion timestamp
        duration_seconds: Total execution time
        records_processed: Number of records processed
        records_failed: Number of records that failed
        quality_score: Overall data quality score (0-1)
        success: Whether pipeline completed successfully
        error_message: Error details if failed
    """
    pipeline_name: str
    execution_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    records_processed: int = 0
    records_failed: int = 0
    quality_score: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate of processed records."""
        total = self.records_processed + self.records_failed
        if total == 0:
            return 0.0
        return self.records_processed / total
    
    @property
    def throughput_per_second(self) -> float:
        """Calculate records processed per second."""
        if not self.duration_seconds or self.duration_seconds == 0:
            return 0.0
        return self.records_processed / self.duration_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for serialization."""
        data = asdict(self)
        data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        data['success_rate'] = f"{self.success_rate:.2%}"
        data['throughput_per_second'] = round(self.throughput_per_second, 2)
        return data


@dataclass
class DataQualityMetrics:
    """
    Metrics for data quality checks.
    
    Tracks quality scores and check results.
    
    Attributes:
        dataset: Name of the dataset checked
        checked_at: Timestamp of quality check
        overall_score: Overall quality score (0-1)
        dimension_scores: Scores per quality dimension
        total_records: Number of records checked
        failed_checks: List of failed check names
        warnings: List of warnings
    """
    dataset: str
    checked_at: datetime
    overall_score: float
    dimension_scores: Dict[str, float]
    total_records: int
    failed_checks: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def passed(self) -> bool:
        """Check if quality meets threshold."""
        return len(self.failed_checks) == 0
    
    @property
    def quality_grade(self) -> str:
        """Get letter grade for quality score."""
        if self.overall_score >= 0.95:
            return "A"
        elif self.overall_score >= 0.90:
            return "B"
        elif self.overall_score >= 0.80:
            return "C"
        elif self.overall_score >= 0.70:
            return "D"
        else:
            return "F"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        data = asdict(self)
        data['checked_at'] = self.checked_at.isoformat()
        data['passed'] = self.passed
        data['quality_grade'] = self.quality_grade
        return data


@dataclass
class PerformanceMetrics:
    """
    Performance metrics for pipeline operations.
    
    Tracks execution times and resource usage.
    
    Attributes:
        operation: Name of the operation
        execution_id: Unique execution identifier
        started_at: Start timestamp
        duration_seconds: Execution duration
        memory_usage_mb: Memory usage in MB
        cpu_usage_percent: CPU usage percentage
        status: Operation status
    """
    operation: str
    execution_id: str
    started_at: datetime
    duration_seconds: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    status: str = "success"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        data = asdict(self)
        data['started_at'] = self.started_at.isoformat()
        return data


class MetricsCollector:
    """
    Central collector for all pipeline metrics.
    
    Aggregates metrics from different sources and provides export capabilities.
    
    Example:
        >>> collector = MetricsCollector()
        >>> 
        >>> # Record pipeline metrics
        >>> collector.record_pipeline_start("brewery_etl", "run_123")
        >>> collector.record_pipeline_complete("run_123", records=1000, quality=0.98)
        >>> 
        >>> # Get metrics
        >>> metrics = collector.get_pipeline_metrics("run_123")
        >>> print(f"Processed {metrics.records_processed} records")
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.logger = logging.getLogger(__name__)
        self._pipeline_metrics: Dict[str, PipelineMetrics] = {}
        self._quality_metrics: List[DataQualityMetrics] = []
        self._performance_metrics: List[PerformanceMetrics] = []
    
    # ==================== Pipeline Metrics ====================
    
    def record_pipeline_start(
        self,
        pipeline_name: str,
        execution_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PipelineMetrics:
        """
        Record pipeline start.
        
        Args:
            pipeline_name: Name of the pipeline
            execution_id: Unique execution ID
            metadata: Optional additional metadata
        
        Returns:
            PipelineMetrics object
        """
        metrics = PipelineMetrics(
            pipeline_name=pipeline_name,
            execution_id=execution_id,
            started_at=datetime.now(),
            metadata=metadata or {}
        )
        
        self._pipeline_metrics[execution_id] = metrics
        
        self.logger.info(
            f"📊 Pipeline started: {pipeline_name} (ID: {execution_id})",
            extra={"execution_id": execution_id, "pipeline": pipeline_name}
        )
        
        return metrics
    
    def record_pipeline_complete(
        self,
        execution_id: str,
        records_processed: int = 0,
        records_failed: int = 0,
        quality_score: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> PipelineMetrics:
        """
        Record pipeline completion.
        
        Args:
            execution_id: Execution ID from record_pipeline_start
            records_processed: Number of successfully processed records
            records_failed: Number of failed records
            quality_score: Overall quality score
            success: Whether pipeline succeeded
            error_message: Error details if failed
        
        Returns:
            Updated PipelineMetrics
        
        Raises:
            ValueError: If execution_id not found
        """
        if execution_id not in self._pipeline_metrics:
            raise ValueError(f"Execution ID not found: {execution_id}")
        
        metrics = self._pipeline_metrics[execution_id]
        metrics.completed_at = datetime.now()
        metrics.duration_seconds = (
            metrics.completed_at - metrics.started_at
        ).total_seconds()
        metrics.records_processed = records_processed
        metrics.records_failed = records_failed
        metrics.quality_score = quality_score
        metrics.success = success
        metrics.error_message = error_message
        
        status_icon = "✅" if success else "❌"
        self.logger.info(
            f"{status_icon} Pipeline completed: {metrics.pipeline_name} "
            f"({metrics.duration_seconds:.2f}s, {records_processed} records)",
            extra={
                "execution_id": execution_id,
                "duration": metrics.duration_seconds,
                "records": records_processed,
                "success": success
            }
        )
        
        return metrics
    
    def get_pipeline_metrics(self, execution_id: str) -> Optional[PipelineMetrics]:
        """Get metrics for a specific pipeline execution."""
        return self._pipeline_metrics.get(execution_id)
    
    def get_all_pipeline_metrics(self) -> List[PipelineMetrics]:
        """Get all pipeline metrics."""
        return list(self._pipeline_metrics.values())
    
    # ==================== Quality Metrics ====================
    
    def record_quality_metrics(
        self,
        dataset: str,
        overall_score: float,
        dimension_scores: Dict[str, float],
        total_records: int,
        failed_checks: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DataQualityMetrics:
        """
        Record data quality metrics.
        
        Args:
            dataset: Name of the dataset
            overall_score: Overall quality score (0-1)
            dimension_scores: Scores per dimension
            total_records: Number of records checked
            failed_checks: List of failed check names
            warnings: List of warnings
            metadata: Additional metadata
        
        Returns:
            DataQualityMetrics object
        """
        metrics = DataQualityMetrics(
            dataset=dataset,
            checked_at=datetime.now(),
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            total_records=total_records,
            failed_checks=failed_checks or [],
            warnings=warnings or [],
            metadata=metadata or {}
        )
        
        self._quality_metrics.append(metrics)
        
        status = "✅ PASSED" if metrics.passed else "❌ FAILED"
        self.logger.info(
            f"📊 Quality check {status}: {dataset} - "
            f"Score: {overall_score:.2%} (Grade: {metrics.quality_grade})",
            extra={
                "dataset": dataset,
                "score": overall_score,
                "grade": metrics.quality_grade,
                "passed": metrics.passed
            }
        )
        
        return metrics
    
    def get_latest_quality_metrics(self, dataset: str) -> Optional[DataQualityMetrics]:
        """Get latest quality metrics for a dataset."""
        dataset_metrics = [m for m in self._quality_metrics if m.dataset == dataset]
        return dataset_metrics[-1] if dataset_metrics else None
    
    def get_all_quality_metrics(self, dataset: Optional[str] = None) -> List[DataQualityMetrics]:
        """Get all quality metrics, optionally filtered by dataset."""
        if dataset:
            return [m for m in self._quality_metrics if m.dataset == dataset]
        return self._quality_metrics
    
    # ==================== Performance Metrics ====================
    
    def record_performance_metrics(
        self,
        operation: str,
        execution_id: str,
        duration_seconds: float,
        memory_usage_mb: Optional[float] = None,
        cpu_usage_percent: Optional[float] = None,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PerformanceMetrics:
        """
        Record performance metrics for an operation.
        
        Args:
            operation: Name of the operation
            execution_id: Unique execution ID
            duration_seconds: Execution duration
            memory_usage_mb: Memory usage
            cpu_usage_percent: CPU usage
            status: Operation status
            metadata: Additional metadata
        
        Returns:
            PerformanceMetrics object
        """
        metrics = PerformanceMetrics(
            operation=operation,
            execution_id=execution_id,
            started_at=datetime.now(),
            duration_seconds=duration_seconds,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            status=status,
            metadata=metadata or {}
        )
        
        self._performance_metrics.append(metrics)
        
        self.logger.debug(
            f"⚡ Performance: {operation} - {duration_seconds:.2f}s",
            extra={
                "operation": operation,
                "duration": duration_seconds,
                "status": status
            }
        )
        
        return metrics
    
    def get_performance_metrics(
        self,
        operation: Optional[str] = None
    ) -> List[PerformanceMetrics]:
        """Get performance metrics, optionally filtered by operation."""
        if operation:
            return [m for m in self._performance_metrics if m.operation == operation]
        return self._performance_metrics
    
    # ==================== Export & Summary ====================
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all collected metrics.
        
        Returns:
            Dictionary with metrics summary
        """
        pipeline_metrics = self.get_all_pipeline_metrics()
        quality_metrics = self.get_all_quality_metrics()
        
        return {
            "pipelines": {
                "total_executions": len(pipeline_metrics),
                "successful": sum(1 for m in pipeline_metrics if m.success),
                "failed": sum(1 for m in pipeline_metrics if not m.success),
                "total_records_processed": sum(m.records_processed for m in pipeline_metrics),
                "avg_duration_seconds": (
                    sum(m.duration_seconds or 0 for m in pipeline_metrics) / len(pipeline_metrics)
                    if pipeline_metrics else 0
                ),
            },
            "quality": {
                "total_checks": len(quality_metrics),
                "passed": sum(1 for m in quality_metrics if m.passed),
                "failed": sum(1 for m in quality_metrics if not m.passed),
                "avg_score": (
                    sum(m.overall_score for m in quality_metrics) / len(quality_metrics)
                    if quality_metrics else 0
                ),
            },
            "performance": {
                "total_operations": len(self._performance_metrics),
                "avg_duration_seconds": (
                    sum(m.duration_seconds for m in self._performance_metrics) / 
                    len(self._performance_metrics)
                    if self._performance_metrics else 0
                ),
            }
        }
    
    def export_metrics(self, format: str = "dict") -> Any:
        """
        Export all metrics in specified format.
        
        Args:
            format: Export format ('dict', 'json')
        
        Returns:
            Metrics in specified format
        """
        data = {
            "summary": self.get_summary(),
            "pipelines": [m.to_dict() for m in self.get_all_pipeline_metrics()],
            "quality": [m.to_dict() for m in self.get_all_quality_metrics()],
            "performance": [m.to_dict() for m in self.get_performance_metrics()],
            "exported_at": datetime.now().isoformat()
        }
        
        if format == "json":
            import json
            return json.dumps(data, indent=2)
        
        return data
    
    def clear_metrics(self) -> None:
        """Clear all collected metrics."""
        self._pipeline_metrics.clear()
        self._quality_metrics.clear()
        self._performance_metrics.clear()
        self.logger.info("Metrics cleared")
    
    def __repr__(self) -> str:
        return (
            f"MetricsCollector("
            f"pipelines={len(self._pipeline_metrics)}, "
            f"quality={len(self._quality_metrics)}, "
            f"performance={len(self._performance_metrics)})"
        )


# Global metrics collector instance (Singleton pattern)
_global_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """
    Get global metrics collector instance (Singleton).
    
    Returns:
        Global MetricsCollector instance
    
    Example:
        >>> collector = get_metrics_collector()
        >>> collector.record_pipeline_start("my_pipeline", "run_001")
    """
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector

