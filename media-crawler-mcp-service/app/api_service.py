# -*- coding: utf-8 -*-
"""FastMCP API 服务模块 - 集成子服务、工具与资源。"""

from __future__ import annotations

from typing import Any

from app.config.settings import Platform, global_settings

from fastmcp import FastMCP
from app.providers.logger import get_logger, init_logger
from app.api.endpoints import main_app, bili_mcp, xhs_mcp
from app.providers.cache.queue import PublishQueue
from app.providers.database.pool_manager import get_pool_manager, close_pool_manager
from app.core.crawler.platforms.xhs.publish import register_xhs_publisher
from app.core.monitoring.metrics import metrics_collector


import asyncio
from contextlib import asynccontextmanager
import time


# 服务启动时间
SERVICE_START_TIME = time.time()

# 创建全局发布队列实例
_publish_queue = PublishQueue()


def create_app() -> tuple[Any, Any]:
    """创建 FastMCP 应用并返回 ASGI 应用。"""

    # 初始化日志
    init_logger(
        name=global_settings.app.name,
        level=global_settings.logger.level,
        log_file=global_settings.logger.log_file,
        enable_file=global_settings.logger.enable_file,
        enable_console=global_settings.logger.enable_console,
        max_file_size=global_settings.logger.max_file_size,
        retention_days=global_settings.logger.retention_days,
    )
    logger = get_logger()

    # 初始化数据库连接池
    async def setup_database():
        try:
            pool_manager = await get_pool_manager()
            pool_status = await pool_manager.get_pool_status()
            logger.info(f"✅ 数据库连接池初始化成功: {pool_status}")
        except Exception as e:
            logger.warning(f"⚠️ 数据库连接池初始化失败: {e}")
            logger.info("继续启动服务，数据库功能将在连接恢复后可用")

    # 挂载子应用到主应用 - 使用 asyncio.run 来处理异步调用
    async def setup_servers():
        await setup_database()
        
        await main_app.import_server(xhs_mcp, 'xhs')
        await main_app.import_server(bili_mcp, 'bili')

        logger.info(f"✅ MCP tools {await main_app.get_tools()}")
        logger.info(f"✅ MCP prompts {await main_app.get_prompts()}")
        logger.info(f"✅ MCP custom_route {main_app._get_additional_http_routes()}")

        await _publish_queue.start_all()
        logger.info("✅ 发布队列管理器已启动")
        
        metrics_collector.update_service_health(
            service_name="mcp_service",
            is_up=True,
            start_time=SERVICE_START_TIME
        )
        logger.info("✅ 监控指标收集器已初始化")

    asyncio.run(setup_servers())

    # 注册发布平台到队列
    register_xhs_publisher(_publish_queue)
    logger.info("✅ 发布平台注册完成")

    # 注册服务工具和资源
    from app.core.prompts import register_prompts
    from app.core.resources import register_resources

    register_prompts(main_app)
    register_resources(main_app)

    # 注册题库页面路由（暂时禁用，FastMCP 不支持直接注册路由）
    # from app.pages.question_bank import register_question_bank_route
    # register_question_bank_route(main_app)
    # logger.info("✅ 题库页面路由已注册")

    logger.info("✅ MCP Prompts 和 Resources 注册成功")
    logger.info("✅ 子服务挂载完成: 小红书MCP(/xhs_), B站MCP(/mcp/bili_)")
    logger.info("✅ CORS 中间件已添加，支持 OPTIONS 请求")
    logger.info(f"✅ {global_settings.app.name} ASGI 应用创建完成")

    # 获取底层的 Starlette 应用
    asgi_app = main_app.http_app(path='/mcp/')


    return asgi_app


# 创建应用并返回
main_asgi = create_app()

