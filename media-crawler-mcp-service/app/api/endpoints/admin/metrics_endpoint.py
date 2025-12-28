# -*- coding: utf-8 -*-
"""Prometheus 指标端点 - 暴露监控指标"""

from __future__ import annotations

from starlette.responses import Response

from app.api.endpoints import main_app
from app.core.monitoring.metrics import metrics_collector


@main_app.custom_route("/metrics", methods=["GET"])
async def metrics(request):
    """
    Prometheus 指标端点
    
    Returns:
        Response: Prometheus 格式的指标数据
    """
    try:
        metrics_collector.update_system_metrics()
        output = metrics_collector.get_metrics()
        return Response(
            content=output,
            media_type="text/plain",
            headers={"Content-Type": "text/plain; version=0.0.4; charset=utf-8"},
        )
    except Exception as exc:
        from app.providers.logger import get_logger
        logger = get_logger()
        logger.error(f"[指标端点] 获取指标失败: {exc}")
        return Response(
            content=f"# 指标获取失败: {exc}\n",
            media_type="text/plain",
            status_code=500,
        )


@main_app.custom_route("/metrics/crawler", methods=["GET"])
async def crawler_metrics(request):
    """
    爬虫专用指标端点
    
    Returns:
        Response: Prometheus 格式的爬虫指标数据
    """
    try:
        metrics_collector.update_system_metrics()
        output = metrics_collector.get_crawler_metrics()
        return Response(
            content=output,
            media_type="text/plain",
            headers={"Content-Type": "text/plain; version=0.0.4; charset=utf-8"},
        )
    except Exception as exc:
        from app.providers.logger import get_logger
        logger = get_logger()
        logger.error(f"[指标端点] 获取爬虫指标失败: {exc}")
        return Response(
            content=f"# 爬虫指标获取失败: {exc}\n",
            media_type="text/plain",
            status_code=500,
        )
