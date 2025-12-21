#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成完整的HTML网页，包含帖子详情
"""

import os
import json
import time
from typing import List, Dict, Any
from xhs_crawler.generators.html_generator import generate_html
from xhs_crawler.core.mcp_utils import load_json_data, save_json_data
from xhs_crawler.core.config import get_output_dir, get_html_file_path


class CompleteHtmlGenerator:
    """
    完整HTML生成器，用于从搜索结果和详情生成HTML
    """
    
    def __init__(self, crawler_type: str = "simple"):
        """
        初始化完整HTML生成器
        
        Args:
            crawler_type: 爬虫类型
        """
        self.crawler_type = crawler_type
        self.output_dir = get_output_dir(crawler_type)
        self.html_file = get_html_file_path(crawler_type)
        self.detail_dir = os.path.join(self.output_dir, "详情")
    
    def load_search_results(self) -> List[Dict[str, Any]]:
        """
        加载搜索结果
        
        Returns:
            帖子列表
        """
        search_file = os.path.join(self.output_dir, "原始响应.json")
        if not os.path.exists(search_file):
            # 尝试加载其他可能的搜索结果文件
            search_file = os.path.join(self.output_dir, "原始搜索结果.json")
            if not os.path.exists(search_file):
                print(f"❌ 搜索结果文件不存在: {search_file}")
                return []
        
        data = load_json_data(search_file)
        if not data:
            return []
        
        search_result = data.get("result", {})
        if search_result.get("code") != 0:
            print(f"❌ 搜索结果无效: {search_result.get('msg')}")
            return []
        
        data = search_result.get("data", {})
        return data.get("notes", [])
    
    def load_post_details(self) -> Dict[str, Dict[str, Any]]:
        """
        加载所有帖子详情
        
        Returns:
            帖子详情字典，key为标题，value为详情
        """
        details = {}
        
        if not os.path.exists(self.detail_dir):
            print(f"❌ 详情目录不存在: {self.detail_dir}")
            return details
        
        # 遍历详情目录
        for filename in os.listdir(self.detail_dir):
            if not filename.endswith("_detail.json"):
                continue
            
            file_path = os.path.join(self.detail_dir, filename)
            try:
                detail = load_json_data(file_path)
                if detail:
                    # 提取标题
                    title = detail.get("basic_info", {}).get("title", "")
                    if title:
                        details[title] = detail
            except Exception as e:
                print(f"❌ 读取详情文件失败: {filename}, {e}")
        
        return details
    
    def prepare_posts_data(self, notes: List[Dict[str, Any]], details: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        准备帖子数据，将搜索结果和详情合并
        
        Args:
            notes: 帖子列表
            details: 帖子详情字典
            
        Returns:
            合并后的帖子数据列表
        """
        posts = []
        
        for note in notes:
            title = note.get("title", "无标题")
            detail = details.get(title, {})
            
            post = {
                "basic_info": note,
                "detail": detail.get("detail", {})
            }
            posts.append(post)
        
        return posts
    
    def run(self):
        """
        运行HTML生成器
        """
        print("🚀 启动完整HTML生成器")
        
        # 1. 加载搜索结果
        notes = self.load_search_results()
        if not notes:
            print("❌ 没有找到搜索结果")
            return
        
        # 2. 加载帖子详情
        details = self.load_post_details()
        print(f"✅ 加载了 {len(details)} 篇帖子详情")
        
        # 3. 准备帖子数据
        posts = self.prepare_posts_data(notes, details)
        
        # 4. 生成HTML网页
        generate_html(posts, self.html_file, "大模型面试经验分享")
        
        print(f"🎉 HTML生成完成！")
        print(f"🌐 HTML网页: {os.path.abspath(self.html_file)}")


def main():
    """
    主函数
    """
    generator = CompleteHtmlGenerator()
    generator.run()


if __name__ == "__main__":
    main()