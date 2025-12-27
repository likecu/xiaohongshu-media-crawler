#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试集成的 AI/ML 功能
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xhs_crawler.core.base_crawler import BaseCrawler


def test_ai_integration():
    """
    测试 AI 功能集成
    
    Returns:
        测试结果
    """
    print("=" * 60)
    print("🧪 测试 AI/ML 功能集成")
    print("=" * 60)
    
    crawler = BaseCrawler(output_dir="test_output")
    
    # 测试 1: 验证 AIUtils 实例是否创建
    print("\n📋 测试 1: 验证 AIUtils 实例...")
    if hasattr(crawler, 'ai_utils'):
        print("✅ AIUtils 实例已创建")
        print(f"   - 类型: {type(crawler.ai_utils).__name__}")
    else:
        print("❌ AIUtils 实例未创建")
        return False
    
    # 测试 2: 验证 TF-IDF 向量化器
    print("\n📋 测试 2: 验证 TF-IDF 向量化器...")
    if hasattr(crawler.ai_utils, 'tfidf_vectorizer'):
        print("✅ TF-IDF 向量化器已初始化")
    else:
        print("❌ TF-IDF 向量化器未初始化")
        return False
    
    # 测试 3: 测试增强内容总结
    print("\n📋 测试 3: 测试增强内容总结...")
    test_content = "这是一篇关于人工智能面试经验的分享文章。"
    test_title = "AI 面试经验总结"
    test_images = []
    
    summary = crawler.ai_utils.summarize_content_enhanced(
        content=test_content,
        title=test_title,
        images=test_images
    )
    
    if summary:
        print("✅ 增强内容总结生成成功")
        print(f"   - 总结: {summary.get('summary', '')[:100]}...")
        print(f"   - 情感: {summary.get('sentiment', '')}")
        print(f"   - 关键信息: {summary.get('key_points', [])}")
    else:
        print("❌ 增强内容总结生成失败")
        return False
    
    # 测试 4: 测试内容索引构建
    print("\n📋 测试 4: 测试内容索引构建...")
    test_posts = [
        {
            "basic_info": {"note_id": "1", "title": "AI 面试技巧与经验分享"},
            "detail": {"desc": "本文分享了人工智能领域面试的实用技巧，包括技术面试准备、项目经验阐述、算法问题解答策略等关键要点。建议面试者提前准备机器学习和深度学习基础知识，熟练掌握常见算法如线性回归、决策树、卷积神经网络等。同时要准备好项目经验介绍，能够清晰阐述项目背景、技术方案、遇到的挑战及解决方案。面试时保持自信，条理清晰，展现良好的沟通能力和学习能力。"}
        },
        {
            "basic_info": {"note_id": "2", "title": "机器学习入门完全指南"},
            "detail": {"desc": "机器学习是人工智能的核心技术之一，本文系统介绍了机器学习的基础知识和入门路径。首先需要掌握数学基础，包括线性代数、概率论、统计学等。然后学习Python编程语言和常用库如NumPy、Pandas、Scikit-learn等。入门阶段建议从监督学习开始，学习分类和回归问题，常用算法包括逻辑回归、支持向量机、随机森林等。实践中可以使用公开数据集如Iris、MNIST等进行练习。建议边学边做，通过实际项目巩固理论知识。"}
        },
        {
            "basic_info": {"note_id": "3", "title": "深度学习实战项目案例分析"},
            "detail": {"desc": "深度学习在计算机视觉、自然语言处理等领域取得了突破性进展。本文通过实际案例介绍深度学习项目的完整流程。以图像分类项目为例，首先进行数据收集和预处理，包括数据增强、归一化等。然后选择合适的模型架构，如ResNet、VGG等，利用迁移学习技术加速训练。训练过程中需要调整超参数，使用交叉验证评估模型性能。最终将模型部署到生产环境，提供API服务。实战中要注意计算资源分配、模型压缩优化、推理速度提升等问题。"}
        }
    ]
    
    try:
        crawler.ai_utils.build_content_index(test_posts)
        print("✅ 内容索引构建成功")
        print(f"   - 索引帖子数: {len(test_posts)}")
        print(f"   - 向量维度: {crawler.ai_utils.post_vectors.shape if crawler.ai_utils.post_vectors is not None else 'N/A'}")
    except Exception as e:
        print(f"❌ 内容索引构建失败: {e}")
        return False
    
    # 测试 5: 测试相似帖子搜索
    print("\n📋 测试 5: 测试相似帖子搜索...")
    try:
        similar = crawler.ai_utils.search_similar_posts("AI面试", top_k=2)
        print(f"✅ 相似帖子搜索成功，找到 {len(similar)} 篇相关帖子")
        for i, post in enumerate(similar):
            print(f"   - {i+1}. {post.get('basic_info', {}).get('title', 'Unknown')} (相似度: {post.get('similarity', 0):.4f})")
    except Exception as e:
        print(f"❌ 相似帖子搜索失败: {e}")
        return False
    
    # 测试 6: 测试帖子推荐
    print("\n📋 测试 6: 测试帖子推荐...")
    try:
        recommendations = crawler.ai_utils.recommend_posts("1", top_k=2)
        print(f"✅ 帖子推荐成功，推荐 {len(recommendations)} 篇帖子")
        for i, post in enumerate(recommendations):
            print(f"   - {i+1}. {post.get('basic_info', {}).get('title', 'Unknown')} (相似度: {post.get('similarity', 0):.4f})")
    except Exception as e:
        print(f"❌ 帖子推荐失败: {e}")
        return False
    
    # 测试 7: 测试趋势分析
    print("\n📋 测试 7: 测试趋势分析...")
    try:
        trends = crawler.ai_utils.analyze_trends(test_posts, time_window="month")
        print("✅ 趋势分析成功")
        print(f"   - 关键词: {trends.get('keywords', [])}")
        print(f"   - 分类: {trends.get('categories', {})}")
    except Exception as e:
        print(f"❌ 趋势分析失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 所有 AI/ML 功能测试通过！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_ai_integration()
    sys.exit(0 if success else 1)
