#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书多关键词爬虫示例

这个示例演示了如何使用多关键词爬虫来爬取小红书上的内容，包括：
1. 初始化爬虫
2. 从配置文件读取搜索关键词
3. 从配置文件读取爬取参数
4. 运行爬虫
5. 处理爬取结果
"""

import json
import os
from typing import List, Dict, Any
from xhs_crawler.crawlers.multi_keyword_crawler import MultiKeywordCrawler


def main():
    """
    主函数，演示多关键词爬虫的完整流程
    """
    print("🎯 小红书多关键词爬虫示例")
    print("=" * 50)
    
    # 1. 初始化爬虫
    print("\n1. 初始化多关键词爬虫...")
    crawler = MultiKeywordCrawler()
    print("✅ 爬虫初始化完成")
    
    # 2. 从配置文件读取搜索关键词和爬取参数
    print("\n2. 从配置文件读取参数...")
    config_file = "search_config.json"
    if not os.path.exists(config_file):
        print(f"❌ 配置文件 {config_file} 不存在")
        return
    
    # 读取配置文件
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # 获取搜索关键词
    keywords: List[str] = config.get("search_terms", ["大模型面试"])
    print(f"📝 搜索关键词: {', '.join(keywords)}")
    
    # 获取爬取参数
    max_pages: int = config.get("page_num", 2)  # 每个关键词爬取的最大页数
    page_size: int = config.get("page_size", 10)  # 每页返回的帖子数量
    print(f"📋 爬取配置: 最大页数={max_pages}, 每页数量={page_size}")
    
    # 4. 运行爬虫
    print("\n4. 启动爬取...")
    try:
        crawler.run(keywords=keywords, max_pages=max_pages, page_size=page_size)
        print("\n✅ 爬取完成！")
        
        # 5. 显示结果信息
        print("\n5. 爬取结果信息:")
        print(f"   📁 结果保存目录: {crawler.output_dir}")
        print(f"   🌐 HTML网页: {crawler.html_file}")
        print(f"   💡 可以在浏览器中打开HTML文件查看完整结果")
        
    except Exception as e:
        print(f"\n❌ 爬取过程中出现错误: {e}")
        print("💡 提示: 请检查网络连接、MCP服务是否正常运行")
    
    print("\n" + "=" * 50)
    print("🎉 示例演示结束")


if __name__ == "__main__":
    main()
