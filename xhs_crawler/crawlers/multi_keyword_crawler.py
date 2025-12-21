#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用多个关键词爬取小红书帖子并生成总结
"""

import time
from typing import List, Dict, Any
from xhs_crawler.core.base_crawler import BaseCrawler
from xhs_crawler.core.config import get_output_dir, get_html_file_path, DEFAULT_CRAWLER_CONFIG


class MultiKeywordCrawler(BaseCrawler):
    """
    多关键词爬虫，继承自BaseCrawler
    """
    
    def __init__(self):
        """
        初始化多关键词爬虫
        """
        output_dir = get_output_dir("multi_keyword")
        super().__init__(output_dir)
        self.html_file = get_html_file_path("multi_keyword")
        self.config = DEFAULT_CRAWLER_CONFIG
    
    def search_posts_by_keyword(self, keyword: str, page_num: int = 1, page_size: int = 10) -> List[Dict[str, Any]]:
        """
        根据关键词搜索小红书帖子
        
        Args:
            keyword: 搜索关键词
            page_num: 页码
            page_size: 每页数量
            
        Returns:
            帖子列表
        """
        return self.search_posts(keyword, page_num, page_size)
    
    def run(self, keywords: List[str] = None, max_pages: int = None, page_size: int = None):
        """
        运行多关键词爬虫
        
        Args:
            keywords: 搜索关键词列表
            max_pages: 爬取的最大页数
            page_size: 每页结果数量
        """
        print("🚀 启动小红书多关键词爬虫")
        start_time = time.time()
        
        # 使用默认值或传入的值
        if keywords is None:
            keywords = ["大模型", "面试", "经验分享"]
        if max_pages is None:
            max_pages = self.config["max_pages"]
        if page_size is None:
            page_size = self.config["page_size"]
        
        all_notes = []
        
        # 对每个关键词进行多页爬取
        for keyword in keywords:
            print(f"\n📌 正在爬取关键词: '{keyword}'")
            for page_num in range(1, max_pages + 1):
                print(f"🔍 正在爬取第 {page_num}/{max_pages} 页")
                notes = self.search_posts_by_keyword(keyword, page_num=page_num, page_size=page_size)
                if not notes:
                    print(f"❌ 第 {page_num} 页没有抓取到任何帖子")
                    break
                
                all_notes.extend(notes)
                print(f"✅ 第 {page_num} 页爬取到 {len(notes)} 篇帖子")
                
                # 避免请求过快
                time.sleep(self.config["sleep_time"])
        
        # 去重
        unique_notes = self.deduplicate_notes(all_notes)
        
        print(f"\n✅ 所有关键词爬取完成，去重后共 {len(unique_notes)} 篇帖子")
        
        if not unique_notes:
            print("❌ 没有抓取到任何帖子")
            return
        
        # 2. 获取帖子详情
        posts = []
        for i, note in enumerate(unique_notes):
            note_id = note.get("note_id")
            if not note_id:
                continue
                
            print(f"\n📌 处理第 {i+1}/{len(unique_notes)} 篇帖子")
            
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
                
                # 保存详情
                title = note.get("title", f"帖子{i+1}")
                clean_title = self._clean_filename(title)
                filename = f"{i+1:03d}_{clean_title}_detail.json"
                self._save_json_data(post, f"{self.detail_dir}/{filename}")
            
            # 避免请求过快
            time.sleep(self.config["sleep_time"])
        
        if not posts:
            print("❌ 没有获取到任何帖子详情")
            return
        
        # 3. 生成HTML网页
        self.generate_html_page(posts, self.html_file, "大模型面试经验分享 - 全量")
        
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
    crawler = MultiKeywordCrawler()
    crawler.run()


if __name__ == "__main__":
    main()