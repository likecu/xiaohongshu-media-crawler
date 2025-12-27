#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件，管理所有项目配置
"""

import os
from typing import List, Dict, Any

# 调试工具端点
INSPECTOR_URL = "http://localhost:9091/api/admin/inspector/execute"

# 默认搜索配置
DEFAULT_SEARCH_CONFIG = {
    "search_terms": [
        "大模型面试 经验分享",
        "大模型面试技巧",
        "大模型面试题",
        "2025 大模型面试",
        "大厂大模型面试",
        "大模型算法面试",
        "大模型应用面试",
        "大模型面试准备",
        "大模型面试经验",
        "大模型面试干货",
        "大模型工程师面试",
        "大模型开发面试",
        "大模型产品面试",
        "大模型运营面试",
        "大模型校招面试",
        "大模型社招面试",
        "大模型面试指南"
    ],
    "page_num": 1,
    "page_size": 10
}

# 默认爬虫配置
DEFAULT_CRAWLER_CONFIG = {
    "max_pages": 3,
    "page_size": 30,
    "sleep_time": 3  # 两次请求之间的睡眠时间
}

# OCR相关配置
OCR_CONFIG = {
    "python_path": "/Users/aaa/python-sdk/python3.13.2/bin/python",
    "tool_path": "/Volumes/600g/app1/doubao获取/python/gemini_ocr.py",
    "question": "图里有什么内容？",
    "max_threads": 4  # 并行处理的最大线程数
}

# 不同爬虫的输出目录配置
OUTPUT_DIR_CONFIG = {
    "simple": "大模型面试帖子",
    "multi_keyword": "大模型面试帖子_all",
    "interview": "大模型面试帖子"
}

# 获取输出目录

def get_output_dir(crawler_type: str = "simple") -> str:
    """
    获取指定爬虫类型的输出目录
    
    Args:
        crawler_type: 爬虫类型
        
    Returns:
        输出目录路径
    """
    return OUTPUT_DIR_CONFIG.get(crawler_type, OUTPUT_DIR_CONFIG["simple"])

# 获取详情目录

def get_detail_dir(crawler_type: str = "simple") -> str:
    """
    获取指定爬虫类型的详情目录
    
    Args:
        crawler_type: 爬虫类型
        
    Returns:
        详情目录路径
    """
    output_dir = get_output_dir(crawler_type)
    return os.path.join(output_dir, "详情")

# 获取HTML文件路径

def get_html_file_path(crawler_type: str = "simple") -> str:
    """
    获取指定爬虫类型的HTML文件路径
    
    Args:
        crawler_type: 爬虫类型
        
    Returns:
        HTML文件路径
    """
    output_dir = get_output_dir(crawler_type)
    if crawler_type == "multi_keyword":
        return os.path.join(output_dir, "大模型面试经验分享_all.html")
    return os.path.join(output_dir, "大模型面试经验分享.html")
