#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书刷题经验分享爬虫脚本
功能：
1. 从配置文件读取刷题相关搜索词
2. 搜索小红书上关于刷题经验、leetcode、算法练习的帖子
3. 获取每个帖子的详细内容
4. 对帖子中的图片进行OCR识别
5. 生成HTML网页展示所有帖子
"""

import os
import json
import time
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from xhs_crawler.core.base_crawler import BaseCrawler
from xhs_crawler.core.config import get_output_dir, get_html_file_path, DEFAULT_SEARCH_CONFIG, OCR_CONFIG
from xhs_crawler.core.mcp_utils import load_json_data, save_json_data
from xhs_crawler.core.local_database import LocalPostgreSQLDatabase


class LeetCodeCrawler(BaseCrawler):
    """
    小红书刷题经验分享爬虫，继承自BaseCrawler
    专注于抓取leetcode、算法刷题相关经验分享
    """
    
    def __init__(self):
        """
        初始化刷题经验爬虫
        """
        output_dir = get_output_dir("leetcode")
        super().__init__(output_dir)
        self.html_file = get_html_file_path("leetcode")
        self.config = self.load_config()
        self.db = None
        self._init_database()
    
    def _init_database(self):
        """
        初始化本地数据库连接
        """
        try:
            self.db = LocalPostgreSQLDatabase(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", 5432)),
                database=os.getenv("DB_NAME", "mcp_tools_db"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "password")
            )
            print("✅ 刷题爬虫数据库初始化成功")
        except Exception as e:
            print(f"⚠️ 数据库初始化失败，将跳过数据库存储: {e}")
            self.db = None
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        config_file = "search_config.json"
        if not os.path.exists(config_file):
            print(f"⚠️ 配置文件不存在: {config_file}")
            return DEFAULT_SEARCH_CONFIG
        
        config = load_json_data(config_file)
        if config:
            print(f"✅ 加载配置文件成功: {config_file}")
            print(f"📋 搜索词数量: {len(config.get('search_terms', []))}")
            return config
        else:
            print(f"⚠️ 加载配置文件失败，使用默认配置")
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
    
    def _extract_question_info(self, note: Dict, detail: Dict) -> Optional[Dict[str, Any]]:
        """
        从帖子中提取题目相关信息
        
        Args:
            note: 帖子基本信息
            detail: 帖子详情
            
        Returns:
            题目信息字典
        """
        content = detail.get("desc", "")
        title = note.get("title", "")
        note_id = note.get("note_id", "")
        
        if not note_id or len(content) < 30:
            return None
        
        question_id = hashlib.md5(f"{note_id}_{title}".encode()).hexdigest()[:12]
        
        lines = content.strip().split('\n')
        question_lines = []
        answer_lines = []
        is_answer = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if any(keyword in line.lower() for keyword in ['答案', '解答', '解析', '答:', '答案:', 'solution', 'answer']):
                is_answer = True
                continue
            
            if is_answer:
                answer_lines.append(line)
            else:
                question_lines.append(line)
        
        if not answer_lines:
            answer_lines = ["参考答案见原文"]
        
        question_content = '\n'.join(question_lines)
        answer_content = '\n'.join(answer_lines)
        
        difficulty = self._detect_difficulty(title, content)
        question_type = self._detect_question_type(title, content)
        
        return {
            'question_id': question_id,
            'content': question_content,
            'answer': answer_content,
            'category': 'leetcode',
            'difficulty': difficulty,
            'question_type': question_type,
            'source': title,
            'source_url': f"https://www.xiaohongshu.com/explore/{note_id}",
            'note_id': note_id
        }
    
    def _detect_difficulty(self, title: str, content: str) -> str:
        """
        检测题目难度
        
        Args:
            title: 标题
            content: 内容
            
        Returns:
            难度级别
        """
        text = (title + " " + content).lower()
        
        if any(kw in text for kw in ['困难', 'hard', '难题', '地狱']):
            return 'hard'
        elif any(kw in text for kw in ['中等', 'medium', '中等难度']):
            return 'medium'
        elif any(kw in text for kw in ['简单', 'easy', '入门']):
            return 'easy'
        else:
            return 'medium'
    
    def _detect_question_type(self, title: str, content: str) -> str:
        """
        检测题目类型
        
        Args:
            title: 标题
            content: 内容
            
        Returns:
            题目类型
        """
        text = (title + " " + content).lower()
        
        if any(kw in text for kw in ['多选', 'multiple', '选择']):
            return 'multiple_choice'
        elif any(kw in text for kw in ['填空', 'fill']):
            return 'fill_blank'
        elif any(kw in text for kw in ['判断', 'true/false', '对错']):
            return 'true_false'
        else:
            return 'discussion'
    
    def _extract_leetcode_problem(self, title: str, content: str) -> Optional[Dict[str, Any]]:
        """
        从帖子中提取LeetCode题目信息
        
        Args:
            title: 标题
            content: 内容
            
        Returns:
            LeetCode题目信息
        """
        import re
        
        problem_id = None
        problem_name = None
        
        leetcode_patterns = [
            r'LeetCode\s*#?\s*(\d+)',
            r'#(\d+)\s*[·•]\s*',
            r'第\s*(\d+)\s*题',
            r'LC\s*(\d+)',
            r'(\d+)\.\s*[^\s]'
        ]
        
        for pattern in leetcode_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                problem_id = int(match.group(1))
                break
        
        if problem_id:
            name_patterns = [
                r'[·•]\s*([A-Z][a-zA-Z\s]+)',
                r'^\s*(\d+)\.\s*([A-Z][a-zA-Z\s]+)',
                r'Title[:：]\s*([A-Za-z\s]+)'
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    problem_name = match.group(1).strip()
                    break
            
            if not problem_name:
                problem_name = title[:50] if title else f"LeetCode #{problem_id}"
            
            difficulty = self._detect_difficulty(title, content)
            
            return {
                'problem_id': problem_id,
                'problem_name': problem_name,
                'problem_url': f"https://leetcode.cn/problems/{problem_name.lower().replace(' ', '-')}/",
                'difficulty': difficulty
            }
        
        return None
    
    def crawl_posts(self, keywords: str = "leetcode 刷题", page_num: int = 1, page_size: int = 10) -> List[Dict[str, Any]]:
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
    
    def save_to_database(self, note: Dict, detail: Dict) -> bool:
        """
        保存帖子数据到数据库
        
        Args:
            note: 帖子基本信息
            detail: 帖子详情
            
        Returns:
            是否保存成功
        """
        if not self.db:
            return False
        
        title = note.get("title", "")
        content = detail.get("desc", "")
        note_id = note.get("note_id", "")
        
        save_success = True
        
        question_info = self._extract_question_info(note, detail)
        if question_info:
            if not self.db.insert_interview_question(
                question_id=question_info['question_id'],
                content=question_info['content'],
                answer=question_info.get('answer'),
                category=question_info.get('category'),
                difficulty=question_info.get('difficulty'),
                question_type=question_info.get('question_type'),
                explanation=question_info.get('explanation'),
                source=question_info.get('source'),
                source_url=question_info.get('source_url'),
                note_id=question_info.get('note_id')
            ):
                save_success = False
        
        leetcode_problem = self._extract_leetcode_problem(title, content)
        if leetcode_problem:
            difficulty = self._detect_difficulty(title, content)
            
            if not self.db.insert_leetcode_practice(
                note_id=note_id,
                title=title,
                content=content,
                difficulty=difficulty,
                question_id=str(leetcode_problem.get('problem_id', '')),
                question_url=leetcode_problem.get('problem_url'),
                category='leetcode'
            ):
                save_success = False
        
        return save_success
    
    def run(self):
        """
        运行爬虫，从配置文件读取搜索词
        """
        print("🚀 启动小红书刷题经验分享爬虫")
        start_time = time.time()
        
        search_terms = self.config.get("search_terms", ["leetcode 刷题"])
        page_num = self.config.get("page_num", 1)
        page_size = self.config.get("page_size", 10)
        enable_db_storage = self.config.get("enable_db_storage", True)
        
        all_posts = []
        all_notes = []
        seen_note_ids = set()
        total_note_count = 0
        
        for keyword in search_terms:
            print(f"\n🔍 处理搜索词: '{keyword}'")
            
            notes = self.search_posts(keyword, page_num, page_size)
            
            unique_notes = []
            for note in notes:
                note_id = note.get("note_id")
                if note_id and note_id not in seen_note_ids:
                    seen_note_ids.add(note_id)
                    unique_notes.append(note)
                    all_notes.append(note)
            
            print(f"✅ 去重后帖子数量: {len(unique_notes)}")
            total_note_count += len(unique_notes)
            
            if enable_db_storage and self.db:
                self.db.save_practice_record(keyword, "小红书", len(unique_notes))
            
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
                    
                    title = note.get("title", f"帖子{i+1}")
                    clean_title = self._clean_filename(title)
                    filename = f"{len(all_posts):03d}_{clean_title}_detail.json"
                    save_json_data(post, os.path.join(self.detail_dir, filename))
                    
                    post_filename = f"{len(all_posts):03d}_{clean_title}.json"
                    save_json_data(note, os.path.join(self.output_dir, post_filename))
                    
                    if enable_db_storage:
                        self.save_to_database(note, detail)
                
                time.sleep(2)
        
        if not all_posts:
            print("❌ 没有抓取到任何帖子")
            return
        
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
        
        self.generate_html_page(all_posts, self.html_file, "刷题经验分享")
        
        end_time = time.time()
        print(f"🎉 爬虫完成！耗时: {end_time - start_time:.2f} 秒")
        print(f"📁 结果保存目录: {self.output_dir}")
        print(f"🌐 HTML网页: {self.html_file}")
        print(f"📊 共抓取 {len(all_posts)} 篇帖子")
        print(f"📋 共处理 {total_note_count} 条搜索结果")
        
        if self.db:
            self.db.close()
    
    def _clean_filename(self, filename: str) -> str:
        """
        清理文件名
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        invalid_chars = ['/', '\\', ':', '*', '?', '<', '>', '|', '"']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:50]


def main():
    """
    主函数
    """
    crawler = LeetCodeCrawler()
    crawler.run()


if __name__ == "__main__":
    main()
