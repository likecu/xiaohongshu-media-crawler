#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML网页生成工具
"""

import time
from typing import List, Dict, Any


def generate_post_html(post: Dict[str, Any], index: int) -> str:
    """
    生成单个帖子的HTML
    
    Args:
        post: 帖子数据
        index: 帖子索引
        
    Returns:
        单个帖子的HTML字符串
    """
    basic_info = post.get("basic_info", {})
    detail = post.get("detail", {})
    
    title = basic_info.get("title", "无标题")
    note_url = basic_info.get("note_url", "")
    user = basic_info.get("user", {})
    interact_info = basic_info.get("interact_info", {})
    
    # 提取内容
    content = ""
    images = []
    
    if isinstance(detail, dict):
        # 处理不同格式的detail数据
        if "content" in detail:
            content = detail.get("content", "")
            images = detail.get("images", [])
        elif "notes" in detail:
            notes_list = detail.get("notes", [])
            if notes_list:
                first_note = notes_list[0]
                content = first_note.get("content", "")
                images = first_note.get("images", [])
    
    # 生成图片HTML
    images_html = ""
    for img in images:
        img_url = img.get("url", "")
        if img_url:
            images_html += f"<img src='{img_url}' alt='帖子图片' style='width: 100%; height: auto; border-radius: 4px; margin: 5px;'>"
    
    # 生成单个帖子HTML
    post_html = f"""
    <div style='background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); margin-bottom: 30px; padding: 20px; transition: transform 0.3s ease, box-shadow 0.3s ease;'>
        <div>
            <h2 style='font-size: 24px; color: #2c3e50; margin-bottom: 10px;'><a href='{note_url}' target='_blank' style='color: #2c3e50; text-decoration: none;'>{index+1}. {title}</a></h2>
            <div style='display: flex; align-items: center; color: #7f8c8d; font-size: 14px;'>
                <div style='display: flex; align-items: center; margin-right: 20px;'>
                    <img src='{user.get("avatar", "")}' alt='用户头像' style='width: 30px; height: 30px; border-radius: 50%; margin-right: 10px;'>
                    <span style='font-weight: 500; margin-right: 10px;'>{user.get("nickname", "匿名用户")}</span>
                </div>
                <div style='display: flex; gap: 20px;'>
                    <div style='display: flex; align-items: center; gap: 5px;'>👍 {interact_info.get("liked_count", 0)}</div>
                    <div style='display: flex; align-items: center; gap: 5px;'>💾 {interact_info.get("collected_count", 0)}</div>
                    <div style='display: flex; align-items: center; gap: 5px;'>💬 {interact_info.get("comment_count", 0)}</div>
                    <div style='display: flex; align-items: center; gap: 5px;'>🔗 {interact_info.get("share_count", 0)}</div>
                </div>
            </div>
        </div>
        
        {'<div style="margin: 20px 0; line-height: 1.8; color: #555;">' + content + '</div>' if content else ''}
        
        {f"<div style='margin: 20px 0;'>{images_html}</div>" if images_html else ""}
    </div>
    """
    
    return post_html


def generate_html(posts: List[Dict[str, Any]], html_file: str, title: str = "大模型面试经验分享") -> bool:
    """
    生成完整的HTML网页
    
    Args:
        posts: 帖子列表
        html_file: HTML文件路径
        title: 网页标题
        
    Returns:
        是否生成成功
    """
    print(f"📝 生成HTML网页: {title}...")
    
    # 生成帖子HTML
    posts_html = ""
    for i, post in enumerate(posts):
        posts_html += generate_post_html(post, i)
    
    # 生成完整HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            h1 {{ text-align: center; color: #2c3e50; margin-bottom: 30px; padding: 20px 0; border-bottom: 2px solid #3498db; }}
            .footer {{ text-align: center; color: #7f8c8d; padding: 20px 0; margin-top: 50px; border-top: 1px solid #e0e0e0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{title}</h1>
            
            <!-- 帖子列表 -->
            {posts_html}
            
            <div class="footer">
                <p>生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p>共 {len(posts)} 篇帖子</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML网页已生成: {html_file}")
        print(f"📊 共生成 {len(posts)} 篇帖子")
        return True
    except Exception as e:
        print(f"❌ 生成HTML失败: {e}")
        return False
