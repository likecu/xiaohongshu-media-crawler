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
6. HTML生成功能
7. 帖子总结功能
"""

import json
import os
import time
from typing import List, Dict, Any
from xhs_crawler.crawlers.multi_keyword_crawler import MultiKeywordCrawler
from xhs_crawler.generators.generate_complete_html import CompleteHtmlGenerator
from xhs_crawler.generators.generate_html_from_existing import ExistingHtmlGenerator
import subprocess

def print_menu():
    """
    打印功能菜单
    """
    print("=" * 60)
    print("🎯 小红书爬虫与分析工具套件")
    print("=" * 60)
    print("1. 🔍 运行多关键词爬虫")
    print("   - 从配置文件读取搜索关键词")
    print("   - 爬取指定页数的小红书内容")
    print("   - 保存爬取结果到本地")
    print()
    print("2. 📄 从搜索结果生成完整HTML")
    print("   - 加载搜索结果和帖子详情")
    print("   - 生成包含完整帖子信息的HTML网页")
    print()
    print("3. 📂 从现有数据生成HTML")
    print("   - 从已有的搜索结果文件生成HTML")
    print("   - 支持多种搜索结果文件格式")
    print()
    print("4. 📝 对帖子内容进行总结")
    print("   - 使用gemini_ocr.py对帖子内容进行OCR识别")
    print("   - 对帖子内容进行总结")
    print("   - 生成包含总结的HTML网页")
    print()
    print("5. 🔥 提取热门关键词")
    print("   - 从小红书搜索结果中提取热门关键词")
    print("   - 根据帖子热度计算关键词热度分数")
    print("   - 生成热门关键词排行榜")
    print()
    print("0. 🚪 退出程序")
    print("=" * 60)

def run_multi_keyword_crawler():
    """
    运行多关键词爬虫
    """
    print("\n🎯 小红书多关键词爬虫示例")
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
    print("🎉 爬虫演示结束")

def generate_complete_html():
    """
    从搜索结果生成完整HTML
    """
    print("\n📄 从搜索结果生成完整HTML")
    print("=" * 50)
    
    try:
        generator = CompleteHtmlGenerator()
        generator.run()
    except Exception as e:
        print(f"\n❌ 生成HTML过程中出现错误: {e}")
        print("💡 提示: 请确保已运行爬虫并生成了搜索结果")
    
    print("\n" + "=" * 50)
    print("🎉 HTML生成演示结束")

def generate_html_from_existing():
    """
    从现有数据生成HTML
    """
    print("\n📂 从现有数据生成HTML")
    print("=" * 50)
    
    try:
        generator = ExistingHtmlGenerator()
        generator.run()
    except Exception as e:
        print(f"\n❌ 生成HTML过程中出现错误: {e}")
        print("💡 提示: 请确保已运行爬虫并生成了搜索结果")
    
    print("\n" + "=" * 50)
    print("🎉 现有数据HTML生成演示结束")

def summarize_posts():
    """
    对帖子内容进行总结
    """
    print("\n📝 对帖子内容进行总结")
    print("=" * 50)
    
    try:
        # 调用summarize_posts.py脚本
        script_path = os.path.join("xhs_crawler", "summarizers", "summarize_posts.py")
        if os.path.exists(script_path):
            print(f"🔍 执行脚本: {script_path}")
            # 使用cwd参数确保脚本在正确的目录下运行
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=600  # 设置10分钟超时，处理大量帖子需要更长时间
            )
            print(result.stdout)
            if result.stderr:
                print(f"\n❌ 脚本执行错误: {result.stderr}")
        else:
            print(f"❌ 脚本文件不存在: {script_path}")
    except subprocess.TimeoutExpired:
        print("\n❌ 脚本执行超时")
        print("💡 提示: 处理大量帖子可能需要更长时间，可以尝试增加超时时间")
    except Exception as e:
        print(f"\n❌ 总结过程中出现错误: {e}")
        print("💡 提示: 请确保gemini_ocr.py工具路径正确且可执行")
    
    print("\n" + "=" * 50)
    print("🎉 帖子总结演示结束")

def extract_hot_keywords():
    """
    提取热门关键词
    """
    print("\n🔥 提取小红书热门关键词")
    print("=" * 50)
    try:
        import os
        from xhs_crawler.summarizers.hot_keywords import (
            extract_hot_keywords_from_directory,
            display_hot_keywords,
            save_hot_keywords
        )
        
        # 自动检测爬虫输出目录
        output_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and '帖子' in d]
        if output_dirs:
            directory = output_dirs[0]  # 使用第一个找到的目录
            print(f"🔍 自动检测到爬虫输出目录: {directory}")
        else:
            directory = "output"  # 默认目录
            print(f"ℹ️  未检测到爬虫输出目录，使用默认目录: {directory}")
        
        # 提取热门关键词，增加关键词数量
        hot_keywords = extract_hot_keywords_from_directory(directory=directory, top_n=50)
        
        if hot_keywords:
            # 显示热门关键词
            display_hot_keywords(hot_keywords)
            
            # 保存热门关键词
            save_hot_keywords(hot_keywords, "hot_keywords.json")
        else:
            print("未提取到热门关键词")
            
    except ImportError as e:
        print(f"\n❌ 导入模块失败: {e}")
        print("💡 提示: 请检查模块路径是否正确")
    except Exception as e:
        print(f"\n❌ 提取热门关键词过程中出现错误: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 热门关键词提取演示结束")

def main():
    """
    主函数，按顺序执行所有功能
    """
    print("🎯 小红书爬虫与分析工具套件 - 自动执行模式")
    print("=" * 60)
    print("程序将按顺序执行以下功能：")
    print("1. 🔍 运行多关键词爬虫")
    print("2. 📄 从搜索结果生成完整HTML")
    print("3. 📂 从现有数据生成HTML")
    print("4. 📝 对帖子内容进行总结")
    print("5. 🔥 提取热门关键词")
    print("=" * 60)
    
    # 按顺序执行所有功能
    print("\n\n" + "=" * 60)
    print("开始执行功能 1: 🔍 运行多关键词爬虫")
    print("=" * 60)
    run_multi_keyword_crawler()
    
    print("\n\n" + "=" * 60)
    print("开始执行功能 2: 📄 从搜索结果生成完整HTML")
    print("=" * 60)
    generate_complete_html()
    
    print("\n\n" + "=" * 60)
    print("开始执行功能 3: 📂 从现有数据生成HTML")
    print("=" * 60)
    generate_html_from_existing()
    
    print("\n\n" + "=" * 60)
    print("开始执行功能 4: 📝 对帖子内容进行总结")
    print("=" * 60)
    summarize_posts()
    
    print("\n\n" + "=" * 60)
    print("开始执行功能 5: 🔥 提取热门关键词")
    print("=" * 60)
    extract_hot_keywords()
    
    print("\n\n" + "=" * 60)
    print("🎉 所有功能执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
