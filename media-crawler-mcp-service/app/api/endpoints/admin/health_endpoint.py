# -*- coding: utf-8 -*-
"""健康检查端点 - 服务健康状态检查"""

from __future__ import annotations

import time
import psutil
from datetime import datetime
from typing import Dict, Any

from starlette.responses import JSONResponse

from app.api.endpoints import main_app
from app.providers.logger import get_logger
from app.config.settings import global_settings
from app.providers.cache.redis_cache import async_redis_storage

logger = get_logger()

STARTUP_TIME = time.time()


def get_uptime_seconds() -> float:
    """
    获取服务启动时间（秒）
    
    Returns:
        float: 服务运行时间（秒）
    """
    return time.time() - STARTUP_TIME


def format_uptime(seconds: float) -> str:
    """
    格式化运行时间
    
    Args:
        seconds: 运行秒数
    
    Returns:
        str: 格式化的时间字符串
    """
    if seconds < 60:
        return f"{int(seconds)}秒"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}分钟{int(seconds % 60)}秒"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}小时{minutes}分钟"
    else:
        days = int(seconds / 86400)
        hours = int((seconds % 86400) / 3600)
        return f"{days}天{hours}小时"


@main_app.custom_route("/health", methods=["GET"])
async def health_check(request):
    """
    基础健康检查端点
    
    Returns:
        JSONResponse: 健康状态
    """
    try:
        uptime_seconds = get_uptime_seconds()
        
        data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": round(uptime_seconds, 2),
            "uptime_formatted": format_uptime(uptime_seconds),
            "version": "1.0.0",
        }
        
        return JSONResponse(content=data)
    
    except Exception as exc:
        logger.error(f"[健康检查] 健康检查失败: {exc}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(exc),
                "timestamp": datetime.now().isoformat(),
            },
            status_code=503,
        )


@main_app.custom_route("/health/live", methods=["GET"])
async def liveness_probe(request):
    """
   存活探针 - Kubernetes liveness probe 使用
    
    Returns:
        JSONResponse: 存活状态
    """
    return JSONResponse(content={"status": "alive"})


@main_app.custom_route("/health/ready", methods=["GET"])
async def readiness_probe(request):
    """
   就绪探针 - Kubernetes readiness probe 使用
    
    检查服务是否准备好接收流量
    
    Returns:
        JSONResponse: 就绪状态
    """
    try:
        checks = {}
        all_healthy = True
        
        try:
            pong = await async_redis_storage.ping()
            checks["redis"] = "ok" if pong else "error"
            if not pong:
                all_healthy = False
        except Exception as exc:
            checks["redis"] = f"error: {exc}"
            all_healthy = False
        
        uptime_seconds = get_uptime_seconds()
        checks["uptime_seconds"] = round(uptime_seconds, 2)
        
        data = {
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
            "timestamp": datetime.now().isoformat(),
        }
        
        if not all_healthy:
            return JSONResponse(content=data, status_code=503)
        
        return JSONResponse(content=data)
    
    except Exception as exc:
        logger.error(f"[健康检查] 就绪检查失败: {exc}")
        return JSONResponse(
            content={
                "status": "not_ready",
                "error": str(exc),
                "timestamp": datetime.now().isoformat(),
            },
            status_code=503,
        )


@main_app.custom_route("/health/detailed", methods=["GET"])
async def detailed_health_check(request):
    """
    详细健康检查端点
    
    Returns:
        JSONResponse: 详细的健康状态
    """
    try:
        uptime_seconds = get_uptime_seconds()
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        checks = {
            "service": {
                "status": "healthy",
                "uptime_seconds": round(uptime_seconds, 2),
                "uptime_formatted": format_uptime(uptime_seconds),
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": round(memory.used / 1024 / 1024 / 1024, 2),
                "memory_total_gb": round(memory.total / 1024 / 1024 / 1024, 2),
                "disk_percent": disk.percent,
                "disk_used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
                "disk_total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
            },
            "dependencies": {},
        }
        
        try:
            pong = await async_redis_storage.ping()
            checks["dependencies"]["redis"] = {
                "status": "healthy",
                "response": "pong" if pong else "unknown",
            }
        except Exception as exc:
            checks["dependencies"]["redis"] = {
                "status": "unhealthy",
                "error": str(exc),
            }
        
        overall_status = "healthy"
        if cpu_percent > 90:
            overall_status = "degraded"
        if memory.percent > 90:
            overall_status = "degraded"
        if disk.percent > 90:
            overall_status = "degraded"
        
        for dep_name, dep_status in checks["dependencies"].items():
            if dep_status.get("status") == "unhealthy":
                overall_status = "unhealthy"
                break
        
        data = {
            "status": overall_status,
            "checks": checks,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }
        
        status_code = 200 if overall_status == "healthy" else 503
        return JSONResponse(content=data, status_code=status_code)
    
    except Exception as exc:
        logger.error(f"[健康检查] 详细健康检查失败: {exc}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(exc),
                "timestamp": datetime.now().isoformat(),
            },
            status_code=503,
        )
