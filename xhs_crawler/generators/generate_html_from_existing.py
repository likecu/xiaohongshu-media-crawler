#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从已有的搜索结果生成HTML网页
"""

import os
import json
import time
from typing import List, Dict, Any
from xhs_crawler.generators.html_generator import generate_html
from xhs_crawler.core.mcp_utils import load_json_data
from xhs_crawler.core.config import get_output_dir, get_html_file_path


class ExistingHtmlGenerator:
    """
    从已有搜索结果生成HTML的生成器
    """
    
    def __init__(self, crawler_type: str = "simple"):
        """
        初始化生成器
        
        Args:
            crawler_type: 爬虫类型
        """
        self.crawler_type = crawler_type
        self.output_dir = get_output_dir(crawler_type)
        self.html_file = get_html_file_path(crawler_type)
    
    def load_search_results(self) -> List[Dict[str, Any]]:
        """
        加载搜索结果
        
        Returns:
            帖子列表
        """
        # 尝试加载多种可能的搜索结果文件
        search_files = [
            os.path.join(self.output_dir, "原始响应.json"),
            os.path.join(self.output_dir, "原始搜索结果.json"),
            os.path.join(self.output_dir, "all_search_results.json")
        ]
        
        for search_file in search_files:
            if os.path.exists(search_file):
                print(f"🔍 尝试加载搜索结果文件: {search_file}")
                data = load_json_data(search_file)
                if data:
                    # 处理不同格式的搜索结果
                    if "result" in data:
                        # 格式1: {"result": {"code": 0, "data": {"notes": [...]}}}
                        search_result = data.get("result", {})
                        if search_result.get("code") == 0:
                            notes = search_result.get("data", {}).get("notes", [])
                            if notes:
                                print(f"✅ 成功加载 {len(notes)} 篇帖子")
                                return notes
                    elif "notes" in data:
                        # 格式2: {"notes": [...], "total_count": ...}
                        notes = data.get("notes", [])
                        print(f"✅ 成功加载 {len(notes)} 篇帖子")
                        return notes
                    elif isinstance(data, list):
                        # 格式3: [{"note_id": ...}, ...]
                        print(f"✅ 成功加载 {len(data)} 篇帖子")
                        return data
        
        print(f"❌ 没有找到有效的搜索结果文件")
        return []
    
    def run(self):
        """
        运行生成器
        """
        print("🚀 启动从现有数据生成HTML")
        
        # 1. 加载搜索结果
        notes = self.load_search_results()
        if not notes:
            print("❌ 没有找到有效的搜索结果")
            return
        
        # 2. 准备帖子数据
        posts = []
        for note in notes:
            # 构建帖子数据结构，与其他爬虫保持一致
            post = {
                "basic_info": note,
                "detail": {}
            }
            posts.append(post)
        
        # 3. 生成HTML网页
        generate_html(posts, self.html_file, "大模型面试经验分享")
        
        print(f"🎉 HTML生成完成！")
        print(f"🌐 HTML网页: {os.path.abspath(self.html_file)}")


def main():
    """
    主函数
    """
    generator = ExistingHtmlGenerator()
    generator.run()


if __name__ == "__main__":
    main()