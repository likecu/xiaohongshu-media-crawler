#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具调用和公共工具函数
"""

import os
import json
import time
import httpx
from typing import List, Dict, Any, Optional

class MCPUtils:
    """
    MCP工具调用工具类
    """
    
    def __init__(self, inspector_url: str = "http://localhost:9091/api/admin/inspector/execute"):
        """
        初始化MCP工具
        
        Args:
            inspector_url: MCP工具端点URL
        """
        self.inspector_url = inspector_url
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """
        获取异步HTTP客户端
        
        Returns:
            httpx.AsyncClient: 异步HTTP客户端
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self) -> None:
        """
        关闭HTTP客户端
        """
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用MCP工具
        
        Args:
            tool_name: 工具名称
            params: 工具参数
            
        Returns:
            工具返回结果
        """
        data = {
            "tool": tool_name,
            "params": params
        }
        
        try:
            client = await self._get_client()
            response = await client.post(
                self.inspector_url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            result = response.json()
            return result.get("result", {})
        except httpx.RequestError as e:
            print(f"❌ MCP工具调用失败: {tool_name}, {e}")
            return {"code": -1, "msg": str(e)}


def ensure_directory(directory: str) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"✅ 创建目录: {directory}")


def ensure_directories(directories: List[str]) -> None:
    """
    确保多个目录存在
    
    Args:
        directories: 目录路径列表
    """
    for directory in directories:
        ensure_directory(directory)


def save_json_data(data: Any, file_path: str) -> bool:
    """
    保存数据到JSON文件
    
    Args:
        data: 要保存的数据
        file_path: 文件路径
        
    Returns:
        是否保存成功
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 保存数据到: {file_path}")
        return True
    except Exception as e:
        print(f"❌ 保存数据失败: {file_path}, {e}")
        return False


def load_json_data(file_path: str) -> Optional[Any]:
    """
    从JSON文件加载数据
    
    Args:
        file_path: 文件路径
        
    Returns:
        加载的数据，如果失败则返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"❌ JSON文件解析失败: {file_path}, {e}")
        return None
    except IOError as e:
        print(f"❌ 读取文件失败: {file_path}, {e}")
        return None


def clean_filename(filename: str) -> str:
    """
    清理文件名，移除无效字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    invalid_chars = ['/', '\\', ':', '*', '?', '<', '>', '|', '"']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename
