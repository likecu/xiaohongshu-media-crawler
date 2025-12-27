#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热门关键词提取工具

该工具用于从小红书搜索结果中提取热门关键词，通过分析帖子的热度指标（点赞数、收藏数、评论数、分享数）来计算关键词的热度。
"""

import os
import json
import re
from collections import Counter
from typing import List, Dict, Any
from xhs_crawler.core.mcp_utils import load_json_data, save_json_data, ensure_directory


def extract_keywords(text: str) -> List[str]:
    """
    从文本中提取关键词
    
    Args:
        text: 输入文本
        
    Returns:
        关键词列表
    """
    if not text:
        return []
    
    # 使用正则表达式提取中文关键词（1-6个字符，增加关键词数量）
    keywords = re.findall(r'[\u4e00-\u9fa5]{1,6}', text)
    
    # 过滤常见停用词
    stopwords = {
        '的', '了', '和', '是', '在', '我', '有', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你',
        '会', '着', '没有', '看', '好', '自己', '这', '又', '来', '给', '我们', '得', '以', '他们', '时', '地', '后', '天', '但',
        '比', '想', '做', '出', '成', '只', '你', '们', '年', '月', '日', '号', '之', '与', '为', '等', '对', '于', '而', '则',
        '且', '并', '或', '及', '其', '所', '把', '被', '从', '向', '由', '以', '因', '因', '此', '如', '若', '倘', '使', '让',
        '叫', '令', '被', '给', '跟', '同', '与', '向', '往', '朝', '当', '对', '对于', '关于', '替', '为', '为了', '为着', '比',
        '和', '同', '跟', '与', '及', '以及', '并', '并且', '而', '而且', '或', '或者', '不但', '不仅', '不光', '不只', '就是',
        '便', '则', '可是', '但是', '不过', '然而', '却', '其实', '原来', '所以', '因此', '因而', '于是', '既然', '当然', '固然',
        '虽然', '尽管', '宁可', '宁愿', '与其', '不如', '要么', '要不是', '假使', '假如', '如果', '倘若', '要是', '比如', '例如',
        '诸如', '像', '似乎', '好像', '仿佛', '犹如', '如同', '是', '就是', '即', '乃', '也就是', '换句话说', '实际上', '其实',
        '原本', '本来', '的确', '确实', '诚然', '固然', '显然', '显而易见', '看来', '看起来', '由此可见', '总之', '总而言之',
        '综上所述', '概括地说', '一句话', '一言以蔽之', '简单地说', '也就是说', '换句话说', '即', '即是', '等于说', '意思是说',
        '换句话说', '也就是说', '即', '即是', '等于说', '意思是说', '简单地说', '概括地说', '一句话', '一言以蔽之', '综上所述',
        '总而言之', '总之', '由此可见', '看来', '看起来', '显然', '显而易见', '诚然', '确实', '的确', '本来', '原本', '其实',
        '实际上', '也就是', '乃', '即', '就是', '是', '如同', '犹如', '仿佛', '好像', '似乎', '像', '诸如', '例如', '比如', '要是',
        '倘若', '如果', '假如', '假使', '要不是', '要么', '不如', '与其', '宁愿', '宁可', '尽管', '虽然', '固然', '当然', '既然',
        '于是', '因而', '因此', '所以', '原来', '其实', '却', '然而', '不过', '但是', '可是', '则', '便', '就是', '不只', '不光',
        '不仅', '不但', '或者', '或', '而且', '而', '并且', '及', '以及', '与', '跟', '同', '和', '比', '为着', '为了', '为', '替',
        '关于', '对于', '对', '当', '朝', '往', '向', '由', '从', '被', '给', '叫', '令', '让', '使', '倘', '若', '如', '因此', '因',
        '以', '由', '向', '从', '把', '所', '其', '及', '或', '并', '且', '则', '而', '于', '对', '等', '为', '与', '之', '号', '日',
        '月', '年', '们', '你', '只', '成', '出', '做', '想', '比', '但', '天', '后', '地', '时', '他们', '得', '我们', '给', '来',
        '又', '这', '自己', '好', '看', '没有', '着', '会', '你', '去', '要', '说', '到', '很', '也', '上', '一个', '一', '都', '人',
        '不', '就', '有', '我', '在', '是', '和', '了', '的'
    }
    
    filtered_keywords = [keyword for keyword in keywords if keyword not in stopwords]
    
    return filtered_keywords


def calculate_keyword_score(keyword_count: int, interact_info: Dict[str, Any]) -> float:
    """
    计算关键词的热度分数
    
    Args:
        keyword_count: 关键词在帖子中出现的次数
        interact_info: 帖子的互动信息，包含点赞数、收藏数、评论数、分享数
        
    Returns:
        关键词的热度分数
    """
    # 获取互动数据，默认值为0
    liked_count = interact_info.get('liked_count', 0) or 0
    collected_count = interact_info.get('collected_count', 0) or 0
    comment_count = interact_info.get('comment_count', 0) or 0
    share_count = interact_info.get('share_count', 0) or 0
    
    # 计算加权分数
    # 权重：点赞(0.4) + 收藏(0.3) + 评论(0.2) + 分享(0.1)
    base_score = liked_count * 0.4 + collected_count * 0.3 + comment_count * 0.2 + share_count * 0.1
    
    # 根据关键词出现次数调整分数
    score = base_score * (1 + keyword_count * 0.1)
    
    return score


def extract_hot_keywords_from_posts(posts: List[Dict[str, Any]], top_n: int = 20) -> List[Dict[str, Any]]:
    """
    从帖子列表中提取热门关键词
    
    Args:
        posts: 帖子列表，包含帖子的基本信息和详情
        top_n: 返回的热门关键词数量
        
    Returns:
        热门关键词列表，每个关键词包含关键词文本、出现次数、总热度分数
    """
    keyword_scores = {}
    keyword_counts = {}
    
    for post in posts:
        # 获取帖子的标题和正文
        title = post.get('basic_info', {}).get('title', '')
        detail = post.get('detail', {})
        content = detail.get('content', '')
        
        # 合并标题和正文
        full_text = f"{title} {content}"
        
        # 提取关键词
        keywords = extract_keywords(full_text)
        
        # 获取帖子的互动信息
        interact_info = post.get('basic_info', {}).get('interact_info', {})
        
        # 统计关键词出现次数和分数
        keyword_counter = Counter(keywords)
        for keyword, count in keyword_counter.items():
            if keyword not in keyword_scores:
                keyword_scores[keyword] = 0
                keyword_counts[keyword] = 0
            
            # 计算该帖子中该关键词的分数
            score = calculate_keyword_score(count, interact_info)
            keyword_scores[keyword] += score
            keyword_counts[keyword] += count
    
    # 生成热门关键词列表
    hot_keywords = []
    for keyword, total_score in keyword_scores.items():
        hot_keywords.append({
            'keyword': keyword,
            'count': keyword_counts[keyword],
            'score': total_score,
            'average_score': total_score / keyword_counts[keyword] if keyword_counts[keyword] > 0 else 0
        })
    
    # 按总热度分数排序
    hot_keywords.sort(key=lambda x: x['score'], reverse=True)
    
    # 返回前top_n个热门关键词
    return hot_keywords[:top_n]


def extract_hot_keywords_from_directory(directory: str = 'output', top_n: int = 20) -> List[Dict[str, Any]]:
    """
    从指定目录的搜索结果中提取热门关键词
    
    Args:
        directory: 搜索结果目录
        top_n: 返回的热门关键词数量
        
    Returns:
        热门关键词列表
    """
    import glob
    
    # 获取所有帖子详情文件
    detail_files = glob.glob(os.path.join(directory, '详情', '*.json'))
    
    posts = []
    for file_path in detail_files:
        # 加载帖子详情
        post = load_json_data(file_path)
        if post:
            posts.append(post)
    
    if not posts:
        print(f"未找到帖子详情文件，请先运行爬虫")
        return []
    
    # 提取热门关键词
    hot_keywords = extract_hot_keywords_from_posts(posts, top_n)
    
    return hot_keywords


def save_hot_keywords(hot_keywords: List[Dict[str, Any]], output_file: str = 'hot_keywords.json') -> None:
    """
    保存热门关键词到文件
    
    Args:
        hot_keywords: 热门关键词列表
        output_file: 输出文件名
    """
    save_json_data(hot_keywords, output_file)
    print(f"热门关键词已保存到 {output_file}")


def display_hot_keywords(hot_keywords: List[Dict[str, Any]]) -> None:
    """
    显示热门关键词
    
    Args:
        hot_keywords: 热门关键词列表
    """
    print("\n🔥 小红书热门关键词排行榜 🔥")
    print("=" * 60)
    print(f"{'排名':<5} {'关键词':<10} {'出现次数':<10} {'热度分数':<12} {'平均分数':<12}")
    print("=" * 60)
    
    for i, keyword_info in enumerate(hot_keywords, 1):
        print(f"{i:<5} {keyword_info['keyword']:<10} {keyword_info['count']:<10} {keyword_info['score']:<12.2f} {keyword_info['average_score']:<12.2f}")
    
    print("=" * 60)


if __name__ == "__main__":
    # 示例用法
    import argparse
    
    parser = argparse.ArgumentParser(description='提取小红书热门关键词')
    parser.add_argument('--directory', type=str, default='output', help='搜索结果目录')
    parser.add_argument('--top-n', type=int, default=20, help='返回的热门关键词数量')
    parser.add_argument('--output', type=str, default='hot_keywords.json', help='输出文件名')
    
    args = parser.parse_args()
    
    # 提取热门关键词
    hot_keywords = extract_hot_keywords_from_directory(args.directory, args.top_n)
    
    if hot_keywords:
        # 显示热门关键词
        display_hot_keywords(hot_keywords)
        
        # 保存热门关键词
        save_hot_keywords(hot_keywords, args.output)
    else:
        print("未提取到热门关键词")
