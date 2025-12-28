# -*- coding: utf-8 -*-
"""
Prometheus 指标收集器模块
提供系统、数据库、爬虫等各类指标的采集和暴露
"""

import time
import asyncio
import psutil
from typing import Dict, Any, Optional
from functools import wraps
from contextlib import contextmanager

from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, multiprocess, REGISTRY
)

from app.providers.logger import get_logger

logger = get_logger()


class MetricsCollector:
    """
    指标收集器单例
    管理所有 Prometheus 指标
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._init_metrics()
        self._initialized = True
    
    def _init_metrics(self):
        """初始化所有指标"""
        
        # === 系统指标 ===
        self.cpu_percent = Gauge(
            'system_cpu_percent',
            'CPU 使用率百分比',
            ['core']
        )
        
        self.memory_percent = Gauge(
            'system_memory_percent',
            '内存使用率百分比'
        )
        
        self.memory_used_bytes = Gauge(
            'system_memory_used_bytes',
            '已使用内存(bytes)'
        )
        
        self.memory_available_bytes = Gauge(
            'system_memory_available_bytes',
            '可用内存(bytes)'
        )
        
        self.disk_usage_percent = Gauge(
            'system_disk_usage_percent',
            '磁盘使用率百分比'
        )
        
        self.disk_read_bytes = Counter(
            'system_disk_read_bytes',
            '磁盘读取总量(bytes)'
        )
        
        self.disk_write_bytes = Counter(
            'system_disk_write_bytes',
            '磁盘写入总量(bytes)'
        )
        
        self.network_bytes_sent = Counter(
            'system_network_bytes_sent',
            '网络发送总量(bytes)'
        )
        
        self.network_bytes_recv = Counter(
            'system_network_bytes_recv',
            '网络接收总量(bytes)'
        )
        
        self.boot_time = Gauge(
            'system_boot_time_seconds',
            '系统启动时间戳'
        )
        
        self.process_count = Gauge(
            'system_process_count',
            '运行进程数'
        )
        
        self.thread_count = Gauge(
            'system_thread_count',
            '运行线程数'
        )
        
        # === 数据库指标 ===
        self.db_pool_connections = Gauge(
            'db_pool_connections',
            '数据库连接池当前连接数',
            ['pool_name']
        )
        
        self.db_pool_checked_out = Gauge(
            'db_pool_checked_out',
            '数据库连接池已借出连接数',
            ['pool_name']
        )
        
        self.db_pool_waiters = Gauge(
            'db_pool_waiters',
            '数据库连接池等待连接数',
            ['pool_name']
        )
        
        self.db_query_total = Counter(
            'db_query_total',
            '数据库查询总数',
            ['pool_name', 'query_type']
        )
        
        self.db_query_duration_seconds = Histogram(
            'db_query_duration_seconds',
            '数据库查询耗时(秒)',
            ['pool_name', 'query_type'],
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.db_connection_errors = Counter(
            'db_connection_errors_total',
            '数据库连接错误总数',
            ['pool_name']
        )
        
        # === Redis 指标 ===
        self.redis_connected = Gauge(
            'redis_connected',
            'Redis 连接状态(1=连接,0=断开)'
        )
        
        self.redis_key_count = Gauge(
            'redis_key_count',
            'Redis 键数量'
        )
        
        self.redis_memory_used_bytes = Gauge(
            'redis_memory_used_bytes',
            'Redis 已使用内存(bytes)'
        )
        
        self.redis_ops_total = Counter(
            'redis_operations_total',
            'Redis 操作总数',
            ['operation']
        )
        
        self.redis_ops_duration_seconds = Histogram(
            'redis_operations_duration_seconds',
            'Redis 操作耗时(秒)',
            ['operation'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
        )
        
        # === 爬虫指标 ===
        self.crawler_requests_total = Counter(
            'crawler_requests_total',
            '爬虫请求总数',
            ['platform', 'crawler_type']
        )
        
        self.crawler_requests_failed = Counter(
            'crawler_requests_failed_total',
            '爬虫请求失败总数',
            ['platform', 'crawler_type', 'error_type']
        )
        
        self.crawler_requests_duration_seconds = Histogram(
            'crawler_requests_duration_seconds',
            '爬虫请求耗时(秒)',
            ['platform', 'crawler_type'],
            buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
        )
        
        self.crawler_items_total = Counter(
            'crawler_items_total',
            '爬取内容总数',
            ['platform', 'content_type']
        )
        
        self.crawler_items_duplicated = Counter(
            'crawler_items_duplicated_total',
            '爬取重复内容数',
            ['platform', 'dedup_type']
        )
        
        self.crawler_active_concurrent = Gauge(
            'crawler_active_concurrent',
            '当前活跃的爬虫并发数',
            ['platform']
        )
        
        self.crawler_queue_size = Gauge(
            'crawler_queue_size',
            '爬虫队列大小',
            ['platform', 'queue_name']
        )
        
        # === AI/OCR 指标 ===
        self.ai_requests_total = Counter(
            'ai_requests_total',
            'AI 请求总数',
            ['model', 'task_type']
        )
        
        self.ai_requests_failed = Counter(
            'ai_requests_failed_total',
            'AI 请求失败总数',
            ['model', 'task_type', 'error_type']
        )
        
        self.ai_requests_duration_seconds = Histogram(
            'ai_requests_duration_seconds',
            'AI 请求耗时(秒)',
            ['model', 'task_type'],
            buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0]
        )
        
        self.ai_tokens_total = Counter(
            'ai_tokens_total',
            'AI 使用 Token 总数',
            ['model', 'direction']
        )
        
        # === 发布任务指标 ===
        self.publish_tasks_total = Counter(
            'publish_tasks_total',
            '发布任务总数',
            ['platform', 'status']
        )
        
        self.publish_tasks_active = Gauge(
            'publish_tasks_active',
            '当前活跃发布任务数',
            ['platform']
        )
        
        self.publish_tasks_duration_seconds = Histogram(
            'publish_tasks_duration_seconds',
            '发布任务耗时(秒)',
            ['platform'],
            buckets=[5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0, 1800.0]
        )
        
        self.publish_tasks_failed = Counter(
            'publish_tasks_failed_total',
            '发布任务失败总数',
            ['platform', 'error_type']
        )
        
        # === HTTP 指标 ===
        self.http_requests_total = Counter(
            'http_requests_total',
            'HTTP 请求总数',
            ['method', 'endpoint', 'status_code']
        )
        
        self.http_requests_duration_seconds = Histogram(
            'http_requests_duration_seconds',
            'HTTP 请求耗时(秒)',
            ['method', 'endpoint'],
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        # === 服务健康指标 ===
        self.service_up = Gauge(
            'service_up',
            '服务是否正常运行(1=运行,0=停止)',
            ['service_name']
        )
        
        self.service_start_time = Gauge(
            'service_start_time_seconds',
            '服务启动时间戳',
            ['service_name']
        )
        
        self.service_restart_count = Counter(
            'service_restart_count_total',
            '服务重启次数',
            ['service_name']
        )
    
    def update_system_metrics(self):
        """更新系统指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_percent.labels(core='total').set(cpu_percent)
            
            for i, percent in enumerate(psutil.cpu_percent(interval=None, percpu=True)):
                self.cpu_percent.labels(core=f'core_{i}').set(percent)
            
            memory = psutil.virtual_memory()
            self.memory_percent.set(memory.percent)
            self.memory_used_bytes.set(memory.used)
            self.memory_available_bytes.set(memory.available)
            
            disk = psutil.disk_usage('/')
            self.disk_usage_percent.set(disk.percent)
            
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.disk_read_bytes.inc(disk_io.read_bytes)
                self.disk_write_bytes.inc(disk_io.write_bytes)
            
            net_io = psutil.net_io_counters()
            if net_io:
                self.network_bytes_sent.inc(net_io.bytes_sent)
                self.network_bytes_recv.inc(net_io.bytes_recv)
            
            self.boot_time.set(psutil.boot_time())
            self.process_count.set(len(psutil.pids()))
            
            try:
                self.thread_count.set(len(psutil.Process().threads()))
            except Exception:
                pass
                
        except Exception as e:
            logger.error(f"更新系统指标失败: {e}")
    
    def record_db_query(
        self,
        pool_name: str,
        query_type: str,
        duration: float,
        success: bool = True
    ):
        """
        记录数据库查询指标
        
        Args:
            pool_name: 连接池名称
            query_type: 查询类型
            duration: 耗时(秒)
            success: 是否成功
        """
        self.db_query_total.labels(
            pool_name=pool_name,
            query_type=query_type
        ).inc()
        
        self.db_query_duration_seconds.labels(
            pool_name=pool_name,
            query_type=query_type
        ).observe(duration)
        
        if not success:
            self.db_connection_errors.labels(pool_name=pool_name).inc()
    
    def record_crawler_request(
        self,
        platform: str,
        crawler_type: str,
        duration: float,
        success: bool = True,
        items_count: int = 0,
        error_type: str = None
    ):
        """
        记录爬虫请求指标
        
        Args:
            platform: 平台名称
            crawler_type: 爬虫类型
            duration: 耗时(秒)
            success: 是否成功
            items_count: 获取内容数量
            error_type: 错误类型
        """
        self.crawler_requests_total.labels(
            platform=platform,
            crawler_type=crawler_type
        ).inc()
        
        self.crawler_requests_duration_seconds.labels(
            platform=platform,
            crawler_type=crawler_type
        ).observe(duration)
        
        if not success and error_type:
            self.crawler_requests_failed.labels(
                platform=platform,
                crawler_type=crawler_type,
                error_type=error_type
            ).inc()
        
        if items_count > 0:
            self.crawler_items_total.labels(
                platform=platform,
                content_type='total'
            ).inc(items_count)
    
    def record_crawler_duplicate(
        self,
        platform: str,
        dedup_type: str
    ):
        """
        记录重复内容检测指标
        
        Args:
            platform: 平台名称
            dedup_type: 去重类型 (exact/similar)
        """
        self.crawler_items_duplicated.labels(
            platform=platform,
            dedup_type=dedup_type
        ).inc()
    
    def record_ai_request(
        self,
        model: str,
        task_type: str,
        duration: float,
        tokens: int = 0,
        success: bool = True,
        error_type: str = None
    ):
        """
        记录 AI 请求指标
        
        Args:
            model: 模型名称
            task_type: 任务类型
            duration: 耗时(秒)
            tokens: 使用的 Token 数量
            success: 是否成功
            error_type: 错误类型
        """
        self.ai_requests_total.labels(
            model=model,
            task_type=task_type
        ).inc()
        
        self.ai_requests_duration_seconds.labels(
            model=model,
            task_type=task_type
        ).observe(duration)
        
        if tokens > 0:
            self.ai_tokens_total.labels(
                model=model,
                direction='input'
            ).inc(tokens)
        
        if not success and error_type:
            self.ai_requests_failed.labels(
                model=model,
                task_type=task_type,
                error_type=error_type
            ).inc()
    
    def record_publish_task(
        self,
        platform: str,
        status: str,
        duration: float = 0,
        error_type: str = None
    ):
        """
        记录发布任务指标
        
        Args:
            platform: 平台名称
            status: 任务状态
            duration: 耗时(秒)
            error_type: 错误类型
        """
        self.publish_tasks_total.labels(
            platform=platform,
            status=status
        ).inc()
        
        if duration > 0:
            self.publish_tasks_duration_seconds.labels(
                platform=platform
            ).observe(duration)
        
        if status == 'failed' and error_type:
            self.publish_tasks_failed.labels(
                platform=platform,
                error_type=error_type
            ).inc()
    
    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float
    ):
        """
        记录 HTTP 请求指标
        
        Args:
            method: HTTP 方法
            endpoint: 请求端点
            status_code: 状态码
            duration: 耗时(秒)
        """
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        self.http_requests_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def update_service_health(
        self,
        service_name: str,
        is_up: bool,
        start_time: float = None
    ):
        """
        更新服务健康状态
        
        Args:
            service_name: 服务名称
            is_up: 是否正常运行
            start_time: 启动时间戳
        """
        self.service_up.labels(service_name=service_name).set(1 if is_up else 0)
        
        if start_time:
            self.service_start_time.labels(
                service_name=service_name
            ).set(start_time)
    
    def get_metrics(self) -> bytes:
        """获取 Prometheus 指标数据"""
        return generate_latest(REGISTRY)
    
    def get_content_type(self) -> str:
        """获取指标内容类型"""
        return CONTENT_TYPE_LATEST
    
    def get_crawler_metrics(self) -> bytes:
        """获取爬虫专用指标数据"""
        crawler_collectors = [
            self.crawler_requests_total,
            self.crawler_requests_failed,
            self.crawler_requests_duration_seconds,
            self.crawler_items_total,
            self.crawler_items_duplicated,
            self.crawler_active_concurrent,
            self.crawler_queue_size,
        ]
        output = []
        for collector in crawler_collectors:
            try:
                output.append(generate_latest(collector))
            except Exception:
                pass
        return b"".join(output)
    
    def update_redis_metrics(
        self,
        connected: bool,
        key_count: int = None,
        memory_used_bytes: int = None
    ):
        """
        更新 Redis 指标
        
        Args:
            connected: 是否连接
            key_count: 键数量
            memory_used_bytes: 已使用内存
        """
        self.redis_connected.set(1 if connected else 0)
        
        if key_count is not None:
            self.redis_key_count.set(key_count)
        
        if memory_used_bytes is not None:
            self.redis_memory_used_bytes.set(memory_used_bytes)
    
    def update_crawler_concurrent(
        self,
        platform: str,
        concurrent_count: int
    ):
        """
        更新爬虫并发指标
        
        Args:
            platform: 平台名称
            concurrent_count: 并发数
        """
        self.crawler_active_concurrent.labels(
            platform=platform
        ).set(concurrent_count)
    
    def update_crawler_queue(
        self,
        platform: str,
        queue_name: str,
        size: int
    ):
        """
        更新爬虫队列指标
        
        Args:
            platform: 平台名称
            queue_name: 队列名称
            size: 队列大小
        """
        self.crawler_queue_size.labels(
            platform=platform,
            queue_name=queue_name
        ).set(size)
    
    def reset_crawler_metrics(self, platform: str = None):
        """
        重置爬虫指标
        
        Args:
            platform: 平台名称，为None则重置所有
        """
        if platform:
            try:
                self.crawler_requests_total._metrics[('total', platform)]._value.set(0)
            except Exception:
                pass
        else:
            for metric in [
                self.crawler_requests_total,
                self.crawler_requests_failed,
                self.crawler_items_total,
                self.crawler_items_duplicated,
            ]:
                try:
                    for child in metric._metrics.values():
                        child._value.set(0)
                except Exception:
                    pass


def track_crawler_metrics(platform: str, crawler_type: str):
    """
    爬虫请求指标追踪装饰器
    
    Args:
        platform: 平台名称
        crawler_type: 爬虫类型
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                items_count = len(result) if isinstance(result, (list, tuple)) else 1
                metrics = get_metrics_collector()
                metrics.record_crawler_request(
                    platform=platform,
                    crawler_type=crawler_type,
                    duration=duration,
                    success=True,
                    items_count=items_count
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics = get_metrics_collector()
                metrics.record_crawler_request(
                    platform=platform,
                    crawler_type=crawler_type,
                    duration=duration,
                    success=False,
                    error_type=type(e).__name__
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                items_count = len(result) if isinstance(result, (list, tuple)) else 1
                metrics = get_metrics_collector()
                metrics.record_crawler_request(
                    platform=platform,
                    crawler_type=crawler_type,
                    duration=duration,
                    success=True,
                    items_count=items_count
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics = get_metrics_collector()
                metrics.record_crawler_request(
                    platform=platform,
                    crawler_type=crawler_type,
                    duration=duration,
                    success=False,
                    error_type=type(e).__name__
                )
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def track_ai_metrics(model: str, task_type: str):
    """
    AI 请求指标追踪装饰器
    
    Args:
        model: 模型名称
        task_type: 任务类型
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                tokens = kwargs.get('tokens', 0)
                metrics = get_metrics_collector()
                metrics.record_ai_request(
                    model=model,
                    task_type=task_type,
                    duration=duration,
                    tokens=tokens,
                    success=True
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics = get_metrics_collector()
                metrics.record_ai_request(
                    model=model,
                    task_type=task_type,
                    duration=duration,
                    success=False,
                    error_type=type(e).__name__
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                tokens = kwargs.get('tokens', 0)
                metrics = get_metrics_collector()
                metrics.record_ai_request(
                    model=model,
                    task_type=task_type,
                    duration=duration,
                    tokens=tokens,
                    success=True
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics = get_metrics_collector()
                metrics.record_ai_request(
                    model=model,
                    task_type=task_type,
                    duration=duration,
                    success=False,
                    error_type=type(e).__name__
                )
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


_metrics_collector_instance = None


def get_metrics_collector() -> MetricsCollector:
    """获取指标收集器单例"""
    global _metrics_collector_instance
    if _metrics_collector_instance is None:
        _metrics_collector_instance = MetricsCollector()
    return _metrics_collector_instance
