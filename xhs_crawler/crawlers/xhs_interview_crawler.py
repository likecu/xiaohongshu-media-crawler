#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书大模型面试经验分享爬虫脚本
功能：
1. 从配置文件读取多个搜索词
2. 搜索小红书上关于大模型面试经验分享的帖子
3. 获取每个帖子的详细内容
4. 对帖子中的图片进行OCR识别
5. 生成HTML网页展示所有帖子
"""

import os
import json
import time
from typing import List, Dict, Any
from xhs_crawler.core.base_crawler import BaseCrawler
from xhs_crawler.core.config import get_output_dir, get_html_file_path, DEFAULT_SEARCH_CONFIG, OCR_CONFIG
from xhs_crawler.core.mcp_utils import load_json_data, save_json_data


class XhsInterviewCrawler(BaseCrawler):
    """
    小红书大模型面试经验分享爬虫，继承自BaseCrawler
    """
    
    def __init__(self):
        """
        初始化面试经验爬虫
        """
        output_dir = get_output_dir("interview")
        super().__init__(output_dir)
        self.html_file = get_html_file_path("interview")
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        config_file = "search_config.json"
        if not os.path.exists(config_file):
            print(f"⚠️ 配置文件不存在: {config_file}")
            # 返回默认配置
            return DEFAULT_SEARCH_CONFIG
        
        config = load_json_data(config_file)
        if config:
            print(f"✅ 加载配置文件成功: {config_file}")
            print(f"📋 搜索词数量: {len(config.get('search_terms', []))}")
            return config
        else:
            # 返回默认配置
            return DEFAULT_SEARCH_CONFIG
    
    def ocr_image(self, image_path: str) -> str:
        """
        对图片进行OCR识别
        
        Args:
            image_path: 图片路径
            
        Returns:
            OCR识别结果
        """
        ocr_tool = OCR_CONFIG["tool_path"]
        question = OCR_CONFIG["question"]
        
        if not os.path.exists(ocr_tool):
            print(f"⚠️ OCR工具不存在: {ocr_tool}")
            return ""
        
        if not os.path.exists(image_path):
            print(f"⚠️ 图片不存在: {image_path}")
            return ""
        
        print(f"🔍 正在识别图片: {image_path}...")
        
        command = f"python {ocr_tool} {image_path} --question '{question}'"
        try:
            result = os.popen(command).read().strip()
            return result
        except Exception as e:
            print(f"❌ OCR识别失败: {e}")
            return ""
    
    def crawl_posts(self, keywords: str = "大模型面试 经验分享", page_num: int = 1, page_size: int = 10) -> List[Dict[str, Any]]:
        """
        完整抓取流程
        
        Args:
            keywords: 搜索关键词
            page_num: 页码
            page_size: 每页数量
            
        Returns:
            包含详情的帖子列表
        """
        return self.search_posts(keywords, page_num, page_size)
    
    def run(self):
        """
        运行爬虫，从配置文件读取搜索词
        """
        print("🚀 启动小红书大模型面试经验分享爬虫")
        start_time = time.time()
        
        # 从配置文件获取参数
        search_terms = self.config.get("search_terms", ["大模型面试 经验分享"])
        page_num = self.config.get("page_num", 1)
        page_size = self.config.get("page_size", 10)
        
        all_posts = []
        all_notes = []
        seen_note_ids = set()  # 用于去重
        
        # 对每个搜索词进行搜索
        for keyword in search_terms:
            print(f"\n🔍 处理搜索词: '{keyword}'")
            
            # 1. 搜索帖子
            notes = self.search_posts(keyword, page_num, page_size)
            
            # 去重
            unique_notes = []
            for note in notes:
                note_id = note.get("note_id")
                if note_id and note_id not in seen_note_ids:
                    seen_note_ids.add(note_id)
                    unique_notes.append(note)
                    all_notes.append(note)
            
            print(f"✅ 去重后帖子数量: {len(unique_notes)}")
            
            # 2. 获取帖子详情
            for i, note in enumerate(unique_notes):
                note_id = note.get("note_id")
                if not note_id:
                    continue
                    
                print(f"📌 处理第 {i+1}/{len(unique_notes)} 篇帖子")
                
                detail = self.get_post_detail(
                    note_id=note_id,
                    xsec_token=note.get("xsec_token", ""),
                    xsec_source=note.get("xsec_source", "pc_feed")
                )
                
                if detail:
                    post = {
                        "basic_info": note,
                        "detail": detail
                    }
                    all_posts.append(post)
                    
                    # 保存详情
                    title = note.get("title", f"帖子{i+1}")
                    clean_title = self._clean_filename(title)
                    filename = f"{len(all_posts):03d}_{clean_title}_detail.json"
                    save_json_data(post, os.path.join(self.detail_dir, filename))
                    
                    # 保存原始帖子信息
                    post_filename = f"{len(all_posts):03d}_{clean_title}.json"
                    save_json_data(note, os.path.join(self.output_dir, post_filename))
                
                # 避免请求过快
                time.sleep(2)
        
        if not all_posts:
            print("❌ 没有抓取到任何帖子")
            return
        
        # 保存所有搜索结果
        all_search_result = {
            "result": {
                "code": 0,
                "msg": "success",
                "data": {
                    "notes": all_notes,
                    "total_count": len(all_notes),
                    "page_info": {
                        "current_page": page_num,
                        "page_size": page_size,
                        "has_more": False
                    }
                }
            }
        }
        save_json_data(all_search_result, os.path.join(self.output_dir, "all_search_results.json"))
        
        # 2. 生成HTML网页
        self.generate_html_page(all_posts, self.html_file, "大模型面试经验分享")
        
        end_time = time.time()
        print(f"🎉 爬虫完成！耗时: {end_time - start_time:.2f} 秒")
        print(f"📁 结果保存目录: {self.output_dir}")
        print(f"🌐 HTML网页: {self.html_file}")
        print(f"📊 共抓取 {len(all_posts)} 篇帖子")
    
    def _clean_filename(self, filename: str) -> str:
        """
        清理文件名
        """
        invalid_chars = ['/', '\\', ':', '*', '?', '<', '>', '|', '"']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename


def main():
    """
    主函数
    """
    crawler = XhsInterviewCrawler()
    crawler.run()


if __name__ == "__main__":
    main()