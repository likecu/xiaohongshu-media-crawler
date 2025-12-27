#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型面试题库模块
提供题库管理、AI分类和刷题功能
"""

import os
import sys
import json
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from xhs_crawler.core.base_crawler import BaseCrawler
from xhs_crawler.core.ai_utils import AIUtils


class Difficulty(Enum):
    """难度级别"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(Enum):
    """题目类型"""
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_BLANK = "fill_blank"
    TRUE_FALSE = "true_false"
    DISCUSSION = "discussion"


@dataclass
class Question:
    """面试题数据结构"""
    id: str
    content: str
    answer: str
    category: str
    difficulty: str
    question_type: str
    options: List[str] = None
    explanation: str = ""
    source: str = ""
    created_at: str = ""
    
    def __post_init__(self):
        if self.options is None:
            self.options = []


class QuestionBank:
    """
    面试题库管理类
    
    提供题库的构建、存储、分类和刷题功能
    """
    
    def __init__(self, output_dir: str = "question_bank"):
        """
        初始化题库
        
        Args:
            output_dir: 题库存放目录
        """
        self.output_dir = output_dir
        self.questions_file = os.path.join(output_dir, "questions.json")
        self.categories_file = os.path.join(output_dir, "categories.json")
        self.crawler = BaseCrawler(output_dir=output_dir)
        self.ai_utils = AIUtils()
        self.questions: List[Question] = []
        self.categories: Dict[str, Dict[str, Any]] = {}
        self._ensure_output_dirs()
    
    def _ensure_output_dirs(self) -> None:
        """确保输出目录存在"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def crawl_questions(self, keywords: List[str] = None, pages_per_keyword: int = 3) -> List[Question]:
        """
        从小红书抓取面试题
        
        Args:
            keywords: 关键词列表
            pages_per_keyword: 每个关键词抓取的页数
            
        Returns:
            抓取的题目列表
        """
        if keywords is None:
            keywords = [
                "大模型面试题",
                "LLM面试",
                "transformer面试题",
                "深度学习面试",
                "AI算法面试"
            ]
        
        print("=" * 60)
        print("📚 开始抓取面试题库")
        print("=" * 60)
        
        all_questions = []
        
        for keyword in keywords:
            print(f"\n🔍 搜索关键词: {keyword}")
            
            for page in range(1, pages_per_keyword + 1):
                print(f"   📄 第 {page}/{pages_per_keyword} 页...")
                
                notes = self.crawler.search_posts(keywords=keyword, page_num=page, page_size=10)
                
                for note in notes:
                    note_id = note.get("note_id")
                    if not note_id:
                        continue
                    
                    detail = self.crawler.get_post_detail(
                        note_id=note_id,
                        xsec_token=note.get("xsec_token", ""),
                        xsec_source=note.get("xsec_source", "pc_feed")
                    )
                    
                    if not detail:
                        continue
                    
                    content = detail.get("desc", "")
                    title = note.get("title", "")
                    
                    if len(content) < 50:
                        continue
                    
                    question = self._extract_question(note, detail, content, title)
                    if question:
                        all_questions.append(question)
                
                if notes:
                    print(f"   ✅ 处理 {len(notes)} 篇帖子")
        
        print(f"\n🎉 共抓取 {len(all_questions)} 道面试题")
        self.questions = all_questions
        return all_questions
    
    def _extract_question(self, note: Dict, detail: Dict, content: str, title: str) -> Optional[Question]:
        """
        从帖子中提取面试题
        
        Args:
            note: 帖子基本信息
            detail: 帖子详情
            content: 正文内容
            title: 标题
            
        Returns:
            面试题对象
        """
        import hashlib
        from datetime import datetime
        
        note_id = note.get("note_id", "")
        question_id = hashlib.md5(f"{note_id}_{title}".encode()).hexdigest()[:12]
        
        content_clean = content.strip()
        
        lines = content_clean.split('\n')
        question_lines = []
        answer_lines = []
        is_answer = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if any(keyword in line.lower() for keyword in ['答案', '解答', '解析', '答:', '答案:']):
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
        
        return Question(
            id=question_id,
            content=question_content,
            answer=answer_content,
            category="待分类",
            difficulty="medium",
            question_type="discussion",
            source=title,
            created_at=datetime.now().isoformat()
        )
    
    def categorize_questions(self) -> Dict[str, Dict[str, Any]]:
        """
        使用 AI 对题目进行分类
        
        Returns:
            分类结果
        """
        print("\n" + "=" * 60)
        print("🧠 使用 AI 对面试题进行分类")
        print("=" * 60)
        
        if not self.questions:
            print("❌ 没有题目需要分类")
            return {}
        
        category_mapping = {
            "transformer": ["Transformer架构", "Attention机制", "位置编码", "Encoder-Decoder"],
            "llm_fundamentals": ["LLM基础", "大语言模型", "预训练", "微调"],
            "rlhf": ["RLHF", "强化学习", "对齐", "PPO"],
            "rag": ["RAG", "检索增强", "向量数据库", "知识库"],
            "prompt_engineering": ["提示工程", "Prompt", "few-shot"],
            "deployment": ["部署", "推理", "量化", "加速"],
            "coding": ["代码", "实现", "Python", "PyTorch"],
            "math": ["数学", "概率论", "线性代数", "优化"],
            "nlp": ["NLP", "自然语言处理", "分词", "词向量"]
        }
        
        categorized = {}
        
        for i, question in enumerate(self.questions):
            print(f"   📝 处理题目 {i+1}/{len(self.questions)}...")
            
            content = question.content[:500]
            title = question.source
            
            category = self._classify_single_question(content, title, category_mapping)
            
            question.category = category
            
            if category not in categorized:
                categorized[category] = {
                    "name": self._get_category_name(category),
                    "count": 0,
                    "questions": []
                }
            
            categorized[category]["count"] += 1
            categorized[category]["questions"].append(asdict(question))
        
        self.categories = categorized
        print(f"\n✅ 分类完成，共 {len(categorized)} 个类别")
        
        for cat, info in categorized.items():
            print(f"   - {info['name']}: {info['count']} 题")
        
        return categorized
    
    def _classify_single_question(self, content: str, title: str, mapping: Dict[str, List[str]]) -> str:
        """
        分类单个题目
        
        Args:
            content: 题目内容
            title: 题目来源标题
            mapping: 分类映射
            
        Returns:
            分类标签
        """
        text = (title + " " + content).lower()
        
        scores = {}
        for cat, keywords in mapping.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            scores[cat] = score
        
        max_score_cat = max(scores, key=scores.get) if scores else "other"
        
        if scores.get(max_score_cat, 0) == 0:
            return "other"
        
        return max_score_cat
    
    def _get_category_name(self, category: str) -> str:
        """
        获取分类显示名称
        
        Args:
            category: 分类标签
            
        Returns:
            显示名称
        """
        names = {
            "transformer": "Transformer架构",
            "llm_fundamentals": "LLM基础理论",
            "rlhf": "RLHF与对齐",
            "rag": "RAG检索增强",
            "prompt_engineering": "提示工程",
            "deployment": "模型部署",
            "coding": "编程实现",
            "math": "数学基础",
            "nlp": "NLP知识",
            "other": "其他题目"
        }
        return names.get(category, category)
    
    def _get_default_categories(self) -> Dict[str, Dict[str, Any]]:
        """
        获取默认分类定义
        
        Returns:
            默认分类字典，包含分类标签、名称、题目数量和题目列表
        """
        return {
            "transformer": {
                "name": "Transformer架构",
                "count": 0,
                "questions": []
            },
            "llm_fundamentals": {
                "name": "LLM基础理论",
                "count": 0,
                "questions": []
            },
            "rlhf": {
                "name": "RLHF与对齐",
                "count": 0,
                "questions": []
            },
            "rag": {
                "name": "RAG检索增强",
                "count": 0,
                "questions": []
            },
            "prompt_engineering": {
                "name": "提示工程",
                "count": 0,
                "questions": []
            },
            "deployment": {
                "name": "模型部署",
                "count": 0,
                "questions": []
            },
            "coding": {
                "name": "编程实现",
                "count": 0,
                "questions": []
            },
            "math": {
                "name": "数学基础",
                "count": 0,
                "questions": []
            },
            "nlp": {
                "name": "NLP知识",
                "count": 0,
                "questions": []
            },
            "other": {
                "name": "其他题目",
                "count": 0,
                "questions": []
            }
        }
    
    def save(self) -> None:
        """保存题库到文件"""
        print(f"\n💾 保存题库到 {self.output_dir}")
        
        questions_data = [asdict(q) for q in self.questions]
        with open(self.questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)
        
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump(self.categories, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 保存完成")
        print(f"   - 题目总数: {len(self.questions)}")
        print(f"   - 分类数: {len(self.categories)}")
    
    def load(self) -> bool:
        """
        从文件加载题库
        
        Returns:
            是否加载成功
        """
        if not os.path.exists(self.questions_file):
            print(f"❌ 题库文件不存在: {self.questions_file}")
            return False
        
        with open(self.questions_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        self.questions = [Question(**q) for q in questions_data]
        
        if os.path.exists(self.categories_file):
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                self.categories = json.load(f)
        
        print(f"✅ 加载题库成功")
        print(f"   - 题目总数: {len(self.questions)}")
        print(f"   - 分类数: {len(self.categories)}")
        
        return True
    
    def get_practice_questions(self, category: str = None, difficulty: str = None, count: int = 10) -> List[Question]:
        """
        获取刷题题目
        
        Args:
            category: 分类筛选
            difficulty: 难度筛选
            count: 题目数量
            
        Returns:
            随机筛选的题目列表
        """
        filtered = self.questions
        
        if category and category != "all":
            filtered = [q for q in filtered if q.category == category]
        
        if difficulty:
            filtered = [q for q in filtered if q.difficulty == difficulty]
        
        if len(filtered) <= count:
            return filtered
        
        return random.sample(filtered, count)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取题库统计信息
        
        Returns:
            统计信息
        """
        stats = {
            "total": len(self.questions),
            "by_category": {},
            "by_difficulty": {},
            "by_type": {}
        }
        
        for q in self.questions:
            stats["by_category"][q.category] = stats["by_category"].get(q.category, 0) + 1
            stats["by_difficulty"][q.difficulty] = stats["by_difficulty"].get(q.difficulty, 0) + 1
            stats["by_type"][q.question_type] = stats["by_type"].get(q.question_type, 0) + 1
        
        return stats
