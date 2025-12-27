#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库系统 Flask API 服务器
提供题库的 RESTful API 接口
"""

import os
import sys
import json
import threading
from typing import Dict, Any, List
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xhs_crawler.core.question_bank import QuestionBank, Question, Difficulty


app = Flask(__name__, template_folder='templates')
CORS(app)

# 全局题库实例
question_bank: QuestionBank = None
bank_lock = threading.Lock()


def get_bank() -> QuestionBank:
    """
    获取题库实例（线程安全）
    
    Returns:
        QuestionBank: 题库实例
    """
    global question_bank
    if question_bank is None:
        with bank_lock:
            if question_bank is None:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                question_bank = QuestionBank(output_dir=os.path.join(base_dir, "question_bank"))
    return question_bank


def default_json_handler(obj):
    """
    JSON 序列化默认处理器
    
    Args:
        obj: 要序列化的对象
        
    Returns:
        可序列化的对象
    """
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    if hasattr(obj, 'value'):
        return obj.value
    return str(obj)


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    
    Returns:
        JSON: 健康状态
    """
    return jsonify({
        "status": "ok",
        "message": "题库服务运行中",
        "service": "question-bank-api"
    })


@app.route('/api/questions', methods=['GET'])
def get_questions():
    """
    获取题目列表
    
    Query Parameters:
        category (str): 按分类筛选（可选）
        difficulty (str): 按难度筛选（可选）
        count (int): 返回数量限制（默认10）
        shuffle (bool): 是否随机打乱（默认false）
        
    Returns:
        JSON: 题目列表
    """
    bank = get_bank()
    
    category = request.args.get('category', None)
    difficulty = request.args.get('difficulty', None)
    count = request.args.get('count', 10, type=int)
    shuffle_flag = request.args.get('shuffle', 'false').lower() == 'true'
    
    questions = bank.get_practice_questions(
        category=category,
        difficulty=difficulty,
        count=count * 2
    )
    
    if shuffle_flag:
        import random
        random.shuffle(questions)
    else:
        questions = questions[:count]
    
    question_list = []
    for q in questions:
        question_list.append({
            "id": q.id,
            "content": q.content,
            "answer": q.answer,
            "category": q.category,
            "difficulty": q.difficulty,
            "question_type": q.question_type,
            "options": q.options or [],
            "explanation": q.explanation,
            "source": q.source,
            "created_at": q.created_at
        })
    
    return jsonify({
        "success": True,
        "data": question_list,
        "total": len(question_list)
    })


@app.route('/api/questions/<question_id>', methods=['GET'])
def get_question(question_id: str):
    """
    获取单个题目详情
    
    Args:
        question_id (str): 题目ID
        
    Returns:
        JSON: 题目详情
    """
    bank = get_bank()
    
    for q in bank.questions:
        if q.id == question_id:
            return jsonify({
                "success": True,
                "data": {
                    "id": q.id,
                    "content": q.content,
                    "answer": q.answer,
                    "category": q.category,
                    "difficulty": q.difficulty,
                    "question_type": q.question_type,
                    "options": q.options or [],
                    "explanation": q.explanation,
                    "source": q.source,
                    "created_at": q.created_at
                }
            })
    
    return jsonify({
        "success": False,
        "message": "题目不存在"
    }), 404


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """
    获取所有分类
    
    Returns:
        JSON: 分类列表及统计信息
    """
    bank = get_bank()
    
    categories_data = []
    for category_id, category_info in bank.categories.items():
        questions_in_cat = [q for q in bank.questions if q.category == category_id]
        categories_data.append({
            "id": category_id,
            "name": category_info.get("name", category_id),
            "description": category_info.get("description", ""),
            "keywords": category_info.get("keywords", []),
            "question_count": len(questions_in_cat)
        })
    
    return jsonify({
        "success": True,
        "data": categories_data,
        "total": len(categories_data)
    })


@app.route('/api/categories/<category_id>', methods=['GET'])
def get_category(category_id: str):
    """
    获取单个分类详情
    
    Args:
        category_id (str): 分类ID
        
    Returns:
        JSON: 分类详情及题目列表
    """
    bank = get_bank()
    
    if category_id not in bank.categories:
        return jsonify({
            "success": False,
            "message": "分类不存在"
        }), 404
    
    category_info = bank.categories[category_id]
    questions_in_cat = [q for q in bank.questions if q.category == category_id]
    
    return jsonify({
        "success": True,
        "data": {
            "id": category_id,
            "name": category_info.get("name", category_id),
            "description": category_info.get("description", ""),
            "keywords": category_info.get("keywords", []),
            "question_count": len(questions_in_cat),
            "questions": [{
                "id": q.id,
                "content": q.content,
                "difficulty": q.difficulty
            } for q in questions_in_cat]
        }
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    获取题库统计信息
    
    Returns:
        JSON: 统计信息
    """
    bank = get_bank()
    
    total_questions = len(bank.questions)
    total_categories = len(bank.categories)
    
    difficulty_stats = {
        "easy": len([q for q in bank.questions if q.difficulty == "easy"]),
        "medium": len([q for q in bank.questions if q.difficulty == "medium"]),
        "hard": len([q for q in bank.questions if q.difficulty == "hard"])
    }
    
    return jsonify({
        "success": True,
        "data": {
            "total_questions": total_questions,
            "total_categories": total_categories,
            "difficulty_stats": difficulty_stats,
            "storage_path": bank.output_dir
        }
    })


@app.route('/api/crawl', methods=['POST'])
def crawl_questions():
    """
    抓取题目
    
    Request Body:
        keywords (List[str]): 搜索关键词列表
        pages_per_keyword (int): 每个关键词抓取的页数
        
    Returns:
        JSON: 抓取结果
    """
    bank = get_bank()
    
    data = request.get_json() or {}
    keywords = data.get('keywords', ['大模型面试', 'LLM面试', 'Transformer面试'])
    pages_per_keyword = data.get('pages_per_keyword', 3)
    
    try:
        import asyncio
        new_questions = asyncio.run(
            bank.crawl_questions(keywords=keywords, pages_per_keyword=pages_per_keyword)
        )
        
        asyncio.run(bank.categorize_questions())
        bank.save()
        
        return jsonify({
            "success": True,
            "message": f"成功抓取 {len(new_questions)} 道题目",
            "total_questions": len(bank.questions),
            "new_count": len(new_questions)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"抓取失败: {str(e)}"
        }), 500


@app.route('/api/categorize', methods=['POST'])
def categorize_questions():
    """
    对所有未分类题目进行分类
    
    Returns:
        JSON: 分类结果
    """
    bank = get_bank()
    
    try:
        import asyncio
        asyncio.run(bank.categorize_questions())
        bank.save()
        
        return jsonify({
            "success": True,
            "message": "分类完成",
            "total_categories": len(bank.categories),
            "total_questions": len(bank.questions)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"分类失败: {str(e)}"
        }), 500


@app.route('/api/questions/<question_id>/recategorize', methods=['POST'])
def recategorize_question(question_id: str):
    """
    重新分类单个题目
    
    Args:
        question_id (str): 题目ID
        
    Returns:
        JSON: 分类结果
    """
    bank = get_bank()
    
    question = None
    for q in bank.questions:
        if q.id == question_id:
            question = q
            break
    
    if question is None:
        return jsonify({
            "success": False,
            "message": "题目不存在"
        }), 404
    
    try:
        import asyncio
        new_category = asyncio.run(bank.recategorize_question(question))
        bank.save()
        
        return jsonify({
            "success": True,
            "message": "重新分类完成",
            "new_category": new_category
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"重新分类失败: {str(e)}"
        }), 500


@app.route('/api/save', methods=['POST'])
def save_bank():
    """
    保存题库数据
    
    Returns:
        JSON: 保存结果
    """
    bank = get_bank()
    
    try:
        bank.save()
        return jsonify({
            "success": True,
            "message": "保存成功",
            "path": bank.output_dir
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"保存失败: {str(e)}"
        }), 500


@app.route('/api/export', methods=['GET'])
def export_questions():
    """
    导出题目数据
    
    Returns:
        JSON: 题目数据（JSON格式）
    """
    bank = get_bank()
    
    export_data = {
        "questions": [],
        "categories": bank.categories
    }
    
    for q in bank.questions:
        export_data["questions"].append({
            "id": q.id,
            "content": q.content,
            "answer": q.answer,
            "category": q.category,
            "difficulty": q.difficulty,
            "question_type": q.question_type,
            "options": q.options or [],
            "explanation": q.explanation,
            "source": q.source,
            "created_at": q.created_at
        })
    
    return jsonify(export_data)


@app.route('/question_bank')
@app.route('/question_bank/')
@app.route('/question_bank/index')
@app.route('/question_bank/index.html')
def question_bank_page():
    """
    题库刷题页面
    
    Returns:
        HTML: 刷题页面
    """
    return send_from_directory(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xhs_crawler', 'templates'),
        'question_bank.html'
    )


@app.route('/')
def index():
    """
    首页
    
    Returns:
        HTML: 首页
    """
    return send_from_directory(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xhs_crawler', 'templates'),
        'question_bank.html'
    )


@app.errorhandler(404)
def not_found(error):
    """
    404 错误处理
    
    Args:
        error: 错误对象
        
    Returns:
        JSON: 错误信息
    """
    return jsonify({
        "success": False,
        "message": "页面或接口不存在",
        "available_routes": [
            "GET /api/health - 健康检查",
            "GET /api/questions - 获取题目列表",
            "GET /api/questions/<id> - 获取单个题目",
            "GET /api/categories - 获取分类列表",
            "GET /api/categories/<id> - 获取单个分类",
            "GET /api/stats - 获取统计信息",
            "POST /api/crawl - 抓取题目",
            "POST /api/categorize - 分类题目",
            "POST /api/questions/<id>/recategorize - 重新分类题目",
            "POST /api/save - 保存题库",
            "GET /api/export - 导出数据",
            "GET /question_bank - 刷题页面"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """
    500 错误处理
    
    Args:
        error: 错误对象
        
    Returns:
        JSON: 错误信息
    """
    return jsonify({
        "success": False,
        "message": "服务器内部错误"
    }), 500


def init_sample_data():
    """
    初始化示例数据
    
    如果题库为空，则添加一些示例题目
    """
    bank = get_bank()
    
    if len(bank.questions) == 0:
        print("📝 初始化示例题目数据...")
        
        sample_questions = [
            Question(
                id="sample_001",
                content="请解释Transformer模型中注意力机制的工作原理",
                answer="注意力机制允许模型在处理序列时关注最相关的部分。核心计算包括：1）计算Query、Key、Value三个向量；2）计算Query和Key的相似度得到注意力权重；3）用注意力权重对Value进行加权求和。公式为：Attention(Q,K,V) = softmax(QK^T/√d_k)V",
                category="transformer",
                difficulty="medium",
                question_type="discussion",
                explanation="这是一个考察对注意力机制理解深度的问题，需要详细解释计算过程",
                source="示例数据"
            ),
            Question(
                id="sample_002",
                content="Transformer中为什么要使用多头注意力？",
                answer="多头注意力允许模型同时关注来自不同表示子空间的信息。每个头可以学习到不同类型的依赖关系，如语法关系、语义关系等。最后将所有头的输出拼接并线性变换，得到最终的表示",
                category="transformer",
                difficulty="medium",
                question_type="discussion",
                explanation="多头注意力的优势在于能够并行学习多种依赖关系",
                source="示例数据"
            ),
            Question(
                id="sample_003",
                content="BERT和GPT的主要区别是什么？",
                answer="1）模型架构：BERT使用双向Transformer编码器，GPT使用单向Transformer解码器；2）预训练任务：BERT使用MLM（掩码语言模型），GPT使用自回归语言建模；3）应用场景：BERT适合理解类任务，GPT适合生成类任务",
                category="预训练技术",
                difficulty="medium",
                question_type="discussion",
                explanation="需要从架构、预训练方式、应用场景三个维度对比",
                source="示例数据"
            ),
            Question(
                id="sample_004",
                content="什么是位置编码？为什么Transformer需要位置编码？",
                answer="位置编码是为序列中的每个位置提供位置信息的向量。由于Transformer的自注意力机制是位置无关的，需要显式注入位置信息。常用的方法有正弦位置编码（Sinusoidal）和可学习位置编码（Learned）",
                category="transformer",
                difficulty="easy",
                question_type="discussion",
                explanation="位置编码解决了Transformer无法区分序列顺序的问题",
                source="示例数据"
            ),
            Question(
                id="sample_005",
                content="请解释Prompt Engineering的基本概念",
                answer="Prompt Engineering是指设计和优化输入提示（Prompt）以引导大语言模型生成期望输出的技术。包括：1）设计有效的指令；2）使用少样本示例；3）控制输出格式；4）使用思维链提示等技巧。目标是最大化模型的输出质量",
                category="提示工程",
                difficulty="easy",
                question_type="discussion",
                explanation="Prompt Engineering是当前LLM应用的核心技术之一",
                source="示例数据"
            ),
            Question(
                id="sample_006",
                content="解释一下大模型微调的常见方法",
                answer="常见的大模型微调方法包括：1）全参数微调（Fine-tuning）：更新所有参数，效果最好但成本高；2）LoRA：低秩适配，只训练低秩矩阵，大幅减少参数量；3）QLoRA：在4-bit量化基础上进行LoRA微调；4）Prefix Tuning：添加可学习的prefix向量；5）P-tuning：使用可学习的prompt token",
                category="模型微调",
                difficulty="hard",
                question_type="discussion",
                explanation="需要了解各种方法的原理、优缺点和适用场景",
                source="示例数据"
            ),
            Question(
                id="sample_007",
                content="Transformer中的LayerNorm和BatchNorm有什么区别？",
                answer="1）LayerNorm：对单个样本的所有特征进行归一化，不依赖batch size；2）BatchNorm：对batch中所有样本的同一特征进行归一化。Transformer中使用LayerNorm是因为：序列长度可变，batch内样本长度可能不同，LayerNorm更稳定",
                category="transformer",
                difficulty="medium",
                question_type="discussion",
                explanation="这是Transformer架构中的关键组件",
                source="示例数据"
            ),
            Question(
                id="sample_008",
                content="什么是Tokenization？常用的分词方法有哪些？",
                answer="Tokenization是将文本切分成模型可处理的token的过程。常用方法：1）WordPiece（BERT使用）：基于词表的贪心切分；2）Byte-Pair Encoding（BPE）：基于字节对的统计分词；3）SentencePiece：语言无关的分词器，支持未登录词；4）Tiktoken：OpenAI使用的快速分词器",
                category="NLP基础",
                difficulty="easy",
                question_type="discussion",
                explanation="Tokenization是NLP处理的第一步",
                source="示例数据"
            ),
            Question(
                id="sample_009",
                content="解释大模型中的涌现能力（Emergent Abilities）",
                answer="涌现能力是指模型在规模达到一定阈值后，突然展现出在小模型上不具备的能力。例如：复杂推理、思维链推理、零样本学习等。涌现能力的出现原因仍在研究中，可能与模型参数规模、训练数据量、模型架构等因素有关",
                category="大模型理论",
                difficulty="hard",
                question_type="discussion",
                explanation="涌现能力是大模型研究的重要课题",
                source="示例数据"
            ),
            Question(
                id="sample_010",
                content="如何评估大语言模型的效果？常用的评估指标有哪些？",
                answer="评估方法分为：1）自动化指标：困惑度（PPL）、准确率、F1、BLEU、ROUGE等；2）人工评估：有用性、流畅性、事实性、安全性等；3）专门基准：MMLU（知识）、HellaSwag（推理）、HumanEval（代码）、TruthfulQA（真实性）等",
                category="模型评估",
                difficulty="medium",
                question_type="discussion",
                explanation="需要了解不同任务适用的评估指标",
                source="示例数据"
            )
        ]
        
        for q in sample_questions:
            bank.questions.append(q)
        
        bank.categories = bank._get_default_categories()
        bank.save()
        print(f"✅ 已添加 {len(sample_questions)} 道示例题目")


def main():
    """
    主函数，启动API服务器
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='题库系统 API 服务器')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='绑定地址')
    parser.add_argument('--port', type=int, default=9092, help='端口号')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🚀 题库系统 API 服务器启动中...")
    print("=" * 60)
    
    init_sample_data()
    
    print(f"\n🌐 API 服务地址: http://{args.host}:{args.port}")
    print(f"📚 刷题页面: http://{args.host}:{args.port}/question_bank")
    print(f"📊 API 文档: http://{args.host}:{args.port}/api/health")
    print("=" * 60 + "\n")
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
