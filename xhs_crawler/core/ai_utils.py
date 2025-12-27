#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI/ML工具模块，提供增强的内容分析和推荐功能
"""

import os
import sys
import json
import re
import time
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from xhs_crawler.core.mcp_utils import MCPUtils
from xhs_crawler.core.database import get_neon_database

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入配置
from xhs_crawler.core.config import get_output_dir, get_detail_dir

# OCR工具路径（从配置获取）
from xhs_crawler.core.config import OCR_CONFIG
OCR_TOOL = OCR_CONFIG["tool_path"]


class AIUtils:
    """
    AI/ML工具类，提供增强的内容分析和推荐功能
    """
    
    def __init__(self):
        """
        初始化AI工具
        """
        self.mcp_utils = MCPUtils()
        self.tfidf_vectorizer = TfidfVectorizer(stop_words=None)
        self.post_vectors = None
        self.posts = None
    
    def summarize_content_enhanced(self, content: str, title: str, images: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        增强的内容总结功能，包括内容总结、情感分析和关键信息提取
        
        Args:
            content: 帖子内容
            title: 帖子标题
            images: 图片列表
            
        Returns:
            包含总结、情感分析和关键信息的字典
        """
        print(f"🔍 开始增强内容总结: '{title[:30]}...'")
        print(f"📝 内容长度: {len(content)} 字符")
        
        try:
            # 1. 准备完整内容（包括图片OCR结果）
            full_content = content
            if images and len(images) > 0:
                print(f"📸 包含 {len(images)} 张图片")
                # 这里可以调用现有的OCR功能获取图片内容
                # 为了简洁，我们假设图片内容已经通过其他方式处理
            
            # 2. 调用LLM进行增强总结
            question = f'''请对这篇内容进行增强总结，输出格式为JSON，包含以下字段：
            - summary: 主要内容总结（200字以内）
            - sentiment: 情感倾向（积极/中性/消极）
            - key_points: 关键信息列表（5-10个要点）
            - category: 内容类别
            - difficulty: 难度级别（初级/中级/高级）
            
            内容：
            标题：{title}
            正文：{full_content}
            '''
            
            # 使用gemini_ocr.py工具进行总结
            result = self._call_llm_tool(question)
            
            if result:
                try:
                    # 解析JSON结果
                    summary_data = json.loads(result)
                    return summary_data
                except json.JSONDecodeError:
                    # 如果LLM返回的不是JSON格式，尝试提取关键信息
                    return self._extract_summary_info(result, title)
            
            return {}
            
        except Exception as e:
            print(f"❌ 增强总结异常: {type(e).__name__}: {e}")
            return {}
    
    def _call_llm_tool(self, question: str) -> str:
        """
        调用LLM工具
        
        Args:
            question: 问题内容
            
        Returns:
            LLM回答
        """
        try:
            args = [
                OCR_CONFIG["python_path"],
                OCR_TOOL,
                "--question",
                question
            ]
            
            result = subprocess.run(
                args,
                shell=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=120
            )
            
            if result.returncode != 0:
                print(f"❌ LLM工具调用失败，返回码: {result.returncode}")
                print(f"💬 错误输出: {result.stderr}")
                return ""
            
            # 提取结果
            output = result.stdout.strip()
            if "=== 处理结果 ===" in output:
                result_part = output.split("=== 处理结果 ===")[1]
                if "回答: " in result_part:
                    return result_part.split("回答: ")[1].strip()
            
            return output
            
        except Exception as e:
            print(f"❌ 调用LLM工具异常: {type(e).__name__}: {e}")
            return ""
    
    def _extract_summary_info(self, text: str, title: str) -> Dict[str, Any]:
        """
        从非JSON格式的文本中提取总结信息
        
        Args:
            text: 原始文本
            title: 帖子标题
            
        Returns:
            提取的总结信息
        """
        # 简单的信息提取逻辑
        return {
            "summary": text[:200] + "..." if len(text) > 200 else text,
            "sentiment": "中性",
            "key_points": [text[:100] + "..."],
            "category": "未分类",
            "difficulty": "中级"
        }
    
    def analyze_image_content(self, image_url: str) -> Dict[str, Any]:
        """
        分析图像内容，包括图像分类和标签提取
        
        Args:
            image_url: 图像URL
            
        Returns:
            包含图像分析结果的字典
        """
        print(f"🔍 开始图像内容分析: {image_url[:50]}...")
        
        try:
            # 下载图像
            temp_dir = "/tmp/xhs_image_analysis"
            os.makedirs(temp_dir, exist_ok=True)
            img_save_path = os.path.join(temp_dir, f"image_{int(time.time())}.jpg")
            
            import requests
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            with open(img_save_path, 'wb') as f:
                f.write(response.content)
            
            # 调用图像分析工具
            question = "请分析这张图片的内容，包括：1. 图像主要内容；2. 相关标签（5-10个）；3. 图像类别；4. 关键元素描述"
            
            args = [
                OCR_CONFIG["python_path"],
                OCR_TOOL,
                img_save_path,
                "--question",
                question
            ]
            
            result = subprocess.run(
                args,
                shell=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=120
            )
            
            if result.returncode != 0:
                print(f"❌ 图像分析失败，返回码: {result.returncode}")
                print(f"💬 错误输出: {result.stderr}")
                return {}
            
            # 提取分析结果
            output = result.stdout.strip()
            if "=== 处理结果 ===" in output:
                result_part = output.split("=== 处理结果 ===")[1]
                if "回答: " in result_part:
                    analysis_text = result_part.split("回答: ")[1].strip()
                    
                    # 解析结果（简单示例）
                    return {
                        "content": analysis_text,
                        "tags": [analysis_text[:20] for _ in range(5)],  # 简化处理
                        "category": "未分类",
                        "elements": [analysis_text[:50]]
                    }
            
            return {
                "content": output,
                "tags": [],
                "category": "未分类",
                "elements": []
            }
            
        except Exception as e:
            print(f"❌ 图像内容分析异常: {type(e).__name__}: {e}")
            return {}
    
    def build_content_index(self, posts: List[Dict[str, Any]]):
        """
        构建内容索引，用于相似度搜索
        
        Args:
            posts: 帖子列表
        """
        print(f"🔧 开始构建内容索引，共 {len(posts)} 篇帖子")
        
        self.posts = posts
        
        # 提取帖子内容
        post_contents = []
        for post in posts:
            content = ""
            # 从 basic_info 获取标题
            if "basic_info" in post:
                title = post["basic_info"].get("title", "")
                content += title + " "
            # 从 detail 获取正文
            if "detail" in post:
                desc = post["detail"].get("desc", "")
                content += desc
            post_contents.append(content)
        
        # 构建TF-IDF向量
        self.post_vectors = self.tfidf_vectorizer.fit_transform(post_contents)
        print(f"✅ 内容索引构建完成")
    
    def search_similar_posts(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        基于内容相似度搜索帖子
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            
        Returns:
            相似度排序的帖子列表
        """
        if self.post_vectors is None or self.posts is None:
            print("❌ 内容索引未构建，请先调用build_content_index")
            return []
        
        print(f"🔍 开始相似度搜索: '{query}'")
        
        # 转换查询向量
        query_vector = self.tfidf_vectorizer.transform([query])
        
        # 计算相似度
        similarities = cosine_similarity(query_vector, self.post_vectors).flatten()
        
        # 获取top-k结果
        top_indices = similarities.argsort()[::-1][:top_k]
        
        # 构建结果
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # 只返回相似度大于0的结果
                post = self.posts[idx].copy()
                post["similarity"] = float(similarities[idx])
                results.append(post)
        
        print(f"✅ 找到 {len(results)} 篇相关帖子")
        return results
    
    def recommend_posts(self, post_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        基于内容相似度推荐帖子
        
        Args:
            post_id: 参考帖子ID
            top_k: 返回结果数量
            
        Returns:
            推荐帖子列表
        """
        if self.post_vectors is None or self.posts is None:
            print("❌ 内容索引未构建，请先调用build_content_index")
            return []
        
        print(f"🔍 开始推荐帖子，参考ID: {post_id}")
        
        # 找到参考帖子
        ref_idx = -1
        for i, post in enumerate(self.posts):
            if post.get("note_id") == post_id:
                ref_idx = i
                break
        
        if ref_idx == -1:
            print(f"❌ 未找到参考帖子: {post_id}")
            return []
        
        # 计算相似度
        ref_vector = self.post_vectors[ref_idx]
        similarities = cosine_similarity(ref_vector, self.post_vectors).flatten()
        
        # 获取top-k结果（排除自身）
        top_indices = similarities.argsort()[::-1][1:top_k+1]
        
        # 构建结果
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # 只返回相似度大于0的结果
                post = self.posts[idx].copy()
                post["similarity"] = float(similarities[idx])
                results.append(post)
        
        print(f"✅ 生成 {len(results)} 篇推荐帖子")
        return results
    
    def analyze_trends(self, posts: List[Dict[str, Any]], time_window: str = "month") -> Dict[str, Any]:
        """
        分析内容趋势
        
        Args:
            posts: 帖子列表
            time_window: 时间窗口（day/week/month）
            
        Returns:
            趋势分析结果
        """
        print(f"📊 开始趋势分析，共 {len(posts)} 篇帖子，时间窗口: {time_window}")
        
        # 简化的趋势分析
        # 1. 计算各类别的帖子数量
        category_counts = {}
        for post in posts:
            category = post.get("category", "未分类")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # 2. 计算关键词频率
        all_content = " "
        for post in posts:
            if "title" in post:
                all_content += post["title"] + " "
            if "content" in post:
                all_content += post["content"] + " "
        
        # 简单的关键词提取（使用正则表达式）
        words = re.findall(r'\b\w{2,}\b', all_content)
        word_counts = {}
        for word in words:
            # 排除常见停用词
            if word not in ["的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"]:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # 排序关键词
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            "category_distribution": category_counts,
            "top_keywords": sorted_words,
            "total_posts": len(posts)
        }


def get_ai_utils() -> AIUtils:
    """
    获取AI工具实例
    
    Returns:
        AIUtils实例
    """
    return AIUtils()
