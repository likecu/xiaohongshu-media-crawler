#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫基类，包含所有爬虫的共同逻辑
"""

import os
import json
from typing import List, Dict, Any, Optional
from xhs_crawler.core.mcp_utils import MCPUtils, ensure_directory, save_json_data, clean_filename
from xhs_crawler.core.ai_utils import AIUtils
from xhs_crawler.generators.html_generator import generate_html


class BaseCrawler:
    """
    爬虫基类，包含所有爬虫的共同逻辑
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        初始化爬虫
        
        Args:
            output_dir: 输出目录
        """
        self.mcp_utils = MCPUtils()
        self.ai_utils = AIUtils()
        self.output_dir = output_dir
        self.detail_dir = os.path.join(output_dir, "详情")
        self.ensure_output_dirs()
    
    def ensure_output_dirs(self) -> None:
        """
        确保输出目录存在
        """
        ensure_directory(self.output_dir)
        ensure_directory(self.detail_dir)
    
    def search_posts(self, keywords: str = "大模型面试 经验分享", page_num: int = 1, page_size: int = 10) -> List[Dict[str, Any]]:
        """
        搜索小红书帖子
        
        Args:
            keywords: 搜索关键词
            page_num: 页码
            page_size: 每页数量
            
        Returns:
            帖子列表
        """
        print(f"🔍 搜索关键词: '{keywords}'...")
        
        result = self.mcp_utils.call_mcp_tool("xhs_search", {
            "keywords": keywords,
            "page_num": page_num,
            "page_size": page_size
        })
        
        if result.get("code") != 0:
            print(f"❌ 搜索失败: {result.get('msg')}")
            return []
        
        data = result.get("data", {})
        notes = data.get("notes", [])
        print(f"✅ 找到 {len(notes)} 篇帖子")
        
        return notes
    
    def get_post_detail(self, note_id: str, xsec_token: str, xsec_source: str = "pc_feed") -> Dict[str, Any]:
        """
        获取帖子详情
        
        Args:
            note_id: 帖子ID
            xsec_token: 安全令牌
            xsec_source: 来源
            
        Returns:
            帖子详情
        """
        print(f"📋 获取帖子详情: {note_id}...")
        
        result = self.mcp_utils.call_mcp_tool("xhs_crawler_detail", {
            "note_id": note_id,
            "xsec_token": xsec_token,
            "xsec_source": xsec_source
        })
        
        if result.get("code") != 0:
            print(f"❌ 获取帖子详情失败: {result.get('msg')}")
            return {}
        
        data = result.get("data", {})
        notes = data.get("notes", [])
        
        if notes:
            return notes[0]
        
        return {}
    
    def get_post_comments(self, note_id: str, xsec_token: str, page_num: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """
        获取帖子评论
        
        Args:
            note_id: 帖子ID
            xsec_token: 安全令牌
            page_num: 页码
            page_size: 每页数量
            
        Returns:
            评论列表
        """
        print(f"💬 获取帖子评论: {note_id}...")
        
        result = self.mcp_utils.call_mcp_tool("xhs_crawler_comments", {
            "note_id": note_id,
            "xsec_token": xsec_token,
            "page_num": page_num,
            "page_size": page_size
        })
        
        if result.get("code") != 0:
            print(f"❌ 获取评论失败: {result.get('msg')}")
            return []
        
        return result.get("data", {}).get("comments", [])
    
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
        # 1. 搜索帖子
        notes = self.search_posts(keywords, page_num, page_size)
        
        posts = []
        for i, note in enumerate(notes):
            note_id = note.get("note_id")
            if not note_id:
                continue
                
            print(f"\n📌 处理第 {i+1}/{len(notes)} 篇帖子")
            
            # 2. 获取帖子详情
            detail = self.get_post_detail(
                note_id=note_id,
                xsec_token=note.get("xsec_token", ""),
                xsec_source=note.get("xsec_source", "pc_feed")
            )
            
            if detail:
                # 3. 使用 AI 进行内容分析
                print(f"🧠 使用 AI 分析内容...")
                content = detail.get("desc", "")
                title = note.get("title", "")
                images = detail.get("imageList", [])
                
                enhanced_summary = self.ai_utils.summarize_content_enhanced(
                    content=content,
                    title=title,
                    images=images
                )
                
                post = {
                    "basic_info": note,
                    "detail": detail,
                    "enhanced_summary": enhanced_summary
                }
                posts.append(post)
                
                # 保存详情
                title = note.get("title", f"帖子{i+1}")
                clean_title = clean_filename(title)
                filename = f"{i+1:03d}_{clean_title}_detail.json"
                save_json_data(post, os.path.join(self.detail_dir, filename))
            
            # 保存原始帖子信息
            post_filename = f"{i+1:03d}_{clean_title}.json"
            save_json_data(note, os.path.join(self.output_dir, post_filename))
        
        # 4. 构建内容索引用于相似度搜索和推荐
        if posts:
            print(f"📊 构建内容索引...")
            self.ai_utils.build_content_index(posts)
            print(f"✅ 内容索引构建完成，共索引 {len(posts)} 篇帖子")
            
        return posts
    
    def generate_html_page(self, posts: List[Dict[str, Any]], html_file: str, title: str = "大模型面试经验分享") -> bool:
        """
        生成HTML网页
        
        Args:
            posts: 帖子列表
            html_file: HTML文件路径
            title: 网页标题
            
        Returns:
            是否生成成功
        """
        return generate_html(posts, html_file, title)
    
    def deduplicate_notes(self, notes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对帖子列表进行去重
        
        Args:
            notes: 帖子列表
            
        Returns:
            去重后的帖子列表
        """
        seen_note_ids = set()
        unique_notes = []
        
        for note in notes:
            note_id = note.get("note_id")
            if note_id and note_id not in seen_note_ids:
                seen_note_ids.add(note_id)
                unique_notes.append(note)
        
        print(f"✅ 去重前: {len(notes)} 篇，去重后: {len(unique_notes)} 篇")
        return unique_notes
