#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的小红书爬虫脚本，用于抓取大模型面试经验分享帖子
"""

import time
from xhs_crawler.core.base_crawler import BaseCrawler
from xhs_crawler.core.config import get_output_dir, get_html_file_path


class SimpleXhsCrawler(BaseCrawler):
    """
    简单的小红书爬虫，继承自BaseCrawler
    """
    
    def __init__(self):
        """
        初始化简单爬虫
        """
        output_dir = get_output_dir("simple")
        super().__init__(output_dir)
        self.html_file = get_html_file_path("simple")
    
    def run(self, keywords: str = "大模型面试 经验分享", page_num: int = 1, page_size: int = 10):
        """
        运行爬虫
        
        Args:
            keywords: 搜索关键词
            page_num: 页码
            page_size: 每页数量
        """
        print("🚀 启动小红书大模型面试经验分享爬虫")
        start_time = time.time()
        
        # 1. 搜索帖子
        notes = self.search_posts(keywords, page_num, page_size)
        if not notes:
            print("❌ 没有抓取到任何帖子")
            return
        
        # 2. 获取帖子详情
        posts = []
        for i, note in enumerate(notes):
            note_id = note.get("note_id")
            if not note_id:
                continue
                
            print(f"\n📌 处理第 {i+1}/{len(notes)} 篇帖子")
            
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
                posts.append(post)
                
                # 保存帖子和详情
                title = note.get("title", f"帖子{i+1}")
                clean_title = self._clean_filename(title)
                filename = f"{i+1:03d}_{clean_title}_detail.json"
                self._save_json_data(post, f"{self.detail_dir}/{filename}")
                
                # 保存原始帖子
                post_filename = f"{i+1:03d}_{clean_title}.json"
                self._save_json_data(note, f"{self.output_dir}/{post_filename}")
            
            # 避免请求过快
            time.sleep(2)
        
        if not posts:
            print("❌ 没有获取到任何帖子详情")
            return
        
        # 3. 生成HTML网页
        self.generate_html_page(posts, self.html_file, "大模型面试经验分享")
        
        end_time = time.time()
        print(f"🎉 爬虫完成！耗时: {end_time - start_time:.2f} 秒")
        print(f"📁 结果保存目录: {self.output_dir}")
        print(f"🌐 HTML网页: {self.html_file}")
    
    def _clean_filename(self, filename: str) -> str:
        """
        清理文件名
        """
        invalid_chars = ['/', '\\', ':', '*', '?', '<', '>', '|', '"']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def _save_json_data(self, data, file_path):
        """
        保存JSON数据
        """
        from xhs_crawler.core.mcp_utils import save_json_data
        return save_json_data(data, file_path)


def main():
    """
    主函数
    """
    crawler = SimpleXhsCrawler()
    crawler.run(keywords="大模型面试 经验分享", page_num=1, page_size=10)


if __name__ == "__main__":
    main()