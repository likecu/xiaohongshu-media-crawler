# -*- coding: utf-8 -*-
"""监控模块 - 提供系统监控、指标收集和健康检查功能"""

from app.core.monitoring.metrics import (
    MetricsCollector,
    get_metrics_collector,
    track_crawler_metrics,
    track_ai_metrics,
)

metrics_collector = get_metrics_collector()

__all__ = [
    "MetricsCollector",
    "metrics_collector",
    "get_metrics_collector",
    "track_crawler_metrics",
    "track_ai_metrics",
]
