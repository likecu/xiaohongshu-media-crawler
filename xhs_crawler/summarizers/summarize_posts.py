#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用gemini_ocr.py对帖子内容进行总结，并生成包含总结的HTML网页
"""

import os
import json
import time
import subprocess
import requests
from typing import List, Dict, Any

# 结果保存目录
OUTPUT_DIR = "大模型面试帖子"
DETAIL_DIR = os.path.join(OUTPUT_DIR, "详情")
SUMMARY_DIR = os.path.join(OUTPUT_DIR, "总结")
HTML_FILE = os.path.join(OUTPUT_DIR, "大模型面试经验分享_with_summary.html")

# OCR工具路径
OCR_TOOL = "/Volumes/600g/app1/doubao获取/python/gemini_ocr.py"

# 图片OCR结果缓存
OCR_CACHE = {}
OCR_CACHE_FILE = os.path.join(SUMMARY_DIR, "ocr_cache.json")

def ensure_output_dirs():
    """
    确保输出目录存在，并加载OCR缓存
    """
    if not os.path.exists(SUMMARY_DIR):
        os.makedirs(SUMMARY_DIR)
        print(f"✅ 创建总结目录: {SUMMARY_DIR}")
    
    # 加载OCR缓存
    global OCR_CACHE
    if os.path.exists(OCR_CACHE_FILE):
        try:
            with open(OCR_CACHE_FILE, "r", encoding="utf-8") as f:
                OCR_CACHE = json.load(f)
            print(f"✅ 加载OCR缓存成功，共 {len(OCR_CACHE)} 条记录")
        except Exception as e:
            print(f"⚠️ 加载OCR缓存失败: {e}")
            OCR_CACHE = {}


def save_ocr_cache():
    """
    保存OCR缓存到本地
    """
    try:
        with open(OCR_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(OCR_CACHE, f, ensure_ascii=False, indent=2)
        print(f"✅ OCR缓存已保存，共 {len(OCR_CACHE)} 条记录")
    except Exception as e:
        print(f"❌ 保存OCR缓存失败: {e}")


def load_post_details() -> List[Dict[str, Any]]:
    """
    加载所有帖子详情
    
    Returns:
        帖子详情列表
    """
    posts = []
    print(f"📂 开始加载帖子详情，目录: {DETAIL_DIR}")
    
    if not os.path.exists(DETAIL_DIR):
        print(f"❌ 详情目录不存在: {DETAIL_DIR}")
        return posts
    
    # 获取所有详情文件
    detail_files = [f for f in os.listdir(DETAIL_DIR) if f.endswith("_detail.json")]
    print(f"📁 发现 {len(detail_files)} 个详情文件")
    
    # 遍历详情目录
    for filename in detail_files:
        file_path = os.path.join(DETAIL_DIR, filename)
        print(f"📄 正在加载: {filename}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                detail = json.load(f)
            posts.append({
                "filename": filename,
                "data": detail
            })
            print(f"✅ 加载成功: {filename}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {filename}, {e}")
        except UnicodeDecodeError as e:
            print(f"❌ 编码错误: {filename}, {e}")
        except Exception as e:
            print(f"❌ 读取文件失败: {filename}, {e}")
    
    print(f"📊 成功加载 {len(posts)} 个帖子详情，跳过 {len(detail_files) - len(posts)} 个文件")
    return posts

def download_image(image_url: str, save_path: str) -> bool:
    """
    下载图片到本地
    
    Args:
        image_url: 图片URL
        save_path: 保存路径
        
    Returns:
        是否下载成功
    """
    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"❌ 下载图片失败: {image_url}, 错误: {e}")
        return False


def ocr_image(image_path: str, image_url: str = "") -> str:
    """
    对图片进行OCR识别，使用图片URL作为缓存键
    
    Args:
        image_path: 图片路径
        image_url: 图片URL，用于缓存
        
    Returns:
        OCR识别结果
    """
    # 优先使用图片URL作为缓存键
    cache_key = image_url if image_url else image_path
    
    # 检查缓存中是否已有结果
    if cache_key in OCR_CACHE:
        ocr_result = OCR_CACHE[cache_key]
        print(f"✅ 从缓存获取OCR结果，长度: {len(ocr_result)} 字符")
        return ocr_result
    
    print(f"🔍 开始对图片进行OCR识别: {image_path}")
    try:
        # 使用gemini_ocr.py进行图片OCR识别
        command = f"/Users/aaa/python-sdk/python3.13.2/bin/python {OCR_TOOL} {image_path} --question '图里有什么内容？'"
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding="utf-8",
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"❌ 图片OCR识别失败，返回码: {result.returncode}")
            print(f"💬 错误输出: {result.stderr}")
            return ""
        
        # 提取OCR结果
        ocr_output = result.stdout.strip()
        if "=== 处理结果 ===" in ocr_output:
            result_part = ocr_output.split("=== 处理结果 ===")[1]
            if "回答: " in result_part:
                ocr_result = result_part.split("回答: ")[1].strip()
                print(f"✅ 图片OCR识别成功，结果长度: {len(ocr_result)} 字符")
                # 存入缓存
                OCR_CACHE[cache_key] = ocr_result
                return ocr_result
        
        # 如果没有找到标准格式，返回完整输出
        print(f"⚠️  图片OCR结果格式异常")
        # 存入缓存
        OCR_CACHE[cache_key] = ocr_output
        return ocr_output
    except Exception as e:
        print(f"❌ 图片OCR识别异常: {type(e).__name__}: {e}")
        return ""


def summarize_content(content: str, title: str, images: List[Dict[str, Any]] = None) -> str:
    """
    使用gemini_ocr.py对内容进行总结，包括图片OCR结果
    
    Args:
        content: 帖子内容
        title: 帖子标题
        images: 图片列表
        
    Returns:
        总结结果
    """
    print(f"🔍 开始总结: '{title[:30]}...'")
    print(f"📝 内容长度: {len(content)} 字符")
    
    try:
        # 处理图片，获取OCR结果
        full_content = content
        if images and len(images) > 0:
            print(f"📸 开始处理 {len(images)} 张图片")
            
            # 创建临时目录保存图片
            temp_dir = f"/tmp/xhs_post_images/{title[:20].replace(' ', '_')}"
            os.makedirs(temp_dir, exist_ok=True)
            
            for i, img in enumerate(images):
                img_url = img.get("url", "")
                if not img_url:
                    continue
                
                print(f"📥 正在下载第 {i+1}/{len(images)} 张图片: {img_url[:50]}...")
                
                # 下载图片
                img_save_path = os.path.join(temp_dir, f"image_{i+1}.jpg")
                if download_image(img_url, img_save_path):
                    # 对图片进行OCR识别，传递图片URL用于缓存
                    ocr_result = ocr_image(img_save_path, img_url)
                    if ocr_result:
                        full_content += f"\n\n--- 图片 {i+1} OCR结果 ---\n{ocr_result}"
                
                # 避免请求过快
                time.sleep(1)
        
        print(f"📝 完整内容长度: {len(full_content)} 字符")
        
        # 直接调用gemini_ocr.py进行总结，传递问题和完整内容
        print(f"🔧 调用gemini_ocr.py工具进行总结...")
        question = f'请总结这篇大模型面试经验分享的主要内容，提取关键面试经验、技巧和建议\n\n{full_content}'
        command = f"/Users/aaa/python-sdk/python3.13.2/bin/python {OCR_TOOL} --question \"{question}\""
        print(f"💻 执行命令: {command[:100]}...")
        
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding="utf-8",
            timeout=180  # 设置更长的超时时间
        )
        
        if result.returncode != 0:
            print(f"❌ 命令执行失败，返回码: {result.returncode}")
            print(f"💬 错误输出: {result.stderr}")
            return ""
        
        # 提取总结结果
        summary_output = result.stdout.strip()
        # 找到回答部分
        if "=== 处理结果 ===" in summary_output:
            result_part = summary_output.split("=== 处理结果 ===")[1]
            if "回答: " in result_part:
                summary = result_part.split("回答: ")[1].strip()
                print(f"✅ 总结成功，结果长度: {len(summary)} 字符")
                return summary
        
        # 如果没有找到标准格式，返回完整输出
        print(f"⚠️  未找到标准回答格式，返回完整输出")
        return summary_output
    except subprocess.TimeoutExpired:
        print(f"⏱️ 总结超时，超过120秒")
        return ""
    except Exception as e:
        print(f"❌ 总结异常: {type(e).__name__}: {e}")
        return ""

def is_llm_interview_question(summary: str) -> bool:
    """
    使用对话工具判断总结是否是大模型相关的面试题目
    
    Args:
        summary: 帖子内容总结
        
    Returns:
        是否是大模型相关的面试题目
    """
    print(f"🔍 开始判断是否为大模型相关面试题")
    print(f"📝 总结长度: {len(summary)} 字符")
    
    try:
        # 使用对话工具提问
        question = f'请判断以下内容是否是大模型相关的面试题目，只需要回答"是"或"否"\n\n{summary}'
        command = f"/Users/aaa/python-sdk/python3.13.2/bin/python {OCR_TOOL} --question \"{question}\""
        print(f"💻 执行命令: {command[:100]}...")
        
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding="utf-8",
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"❌ 命令执行失败，返回码: {result.returncode}")
            print(f"💬 错误输出: {result.stderr}")
            return False
        
        # 提取判断结果
        output = result.stdout.strip()
        print(f"📋 判断结果输出: {output}")
        
        # 解析回答
        if "=== 处理结果 ===" in output:
            result_part = output.split("=== 处理结果 ===")[1]
            if "回答: " in result_part:
                answer = result_part.split("回答: ")[1].strip().lower()
                print(f"✅ 解析回答: {answer}")
                return "是" in answer or "yes" in answer
        
        # 直接检查输出中是否包含"是"或"yes"
        answer = output.lower()
        print(f"✅ 直接解析回答: {answer}")
        return "是" in answer or "yes" in answer
    except Exception as e:
        print(f"❌ 判断异常: {type(e).__name__}: {e}")
        return False

def save_summary(title: str, summary: str):
    """
    保存总结到本地
    
    Args:
        title: 帖子标题
        summary: 总结内容
    """
    print(f"💾 开始保存总结: '{title[:30]}...'")
    clean_title = title.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace('"', '_')
    summary_file = os.path.join(SUMMARY_DIR, f"{clean_title}_summary.txt")
    print(f"📄 保存路径: {summary_file}")
    
    try:
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"✅ 总结已成功保存: {summary_file}")
        print(f"📊 总结长度: {len(summary)} 字符")
    except Exception as e:
        print(f"❌ 保存总结失败: {e}")
        raise

def generate_html_with_summary(posts: List[Dict[str, Any]], summaries: Dict[str, str]):
    """
    生成包含总结的HTML网页
    
    Args:
        posts: 帖子列表
        summaries: 帖子总结字典
    """
    print(f"📝 开始生成包含总结的HTML网页")
    print(f"📊 总共有 {len(posts)} 篇帖子需要处理")
    print(f"📋 已生成 {len(summaries)} 篇帖子的总结")
    
    # 生成帖子HTML
    posts_html = ""
    processed_count = 0
    summary_count = 0
    
    for i, post_item in enumerate(posts):
        print(f"🔧 正在处理第 {i+1}/{len(posts)} 篇帖子")
        post = post_item.get("data", {})
        basic_info = post.get("basic_info", {})
        detail = post.get("detail", {})
        
        title = basic_info.get("title", "无标题")
        note_url = basic_info.get("note_url", "")
        user = basic_info.get("user", {})
        interact_info = basic_info.get("interact_info", {})
        
        print(f"📄 帖子标题: '{title[:30]}...'")
        
        # 提取内容
        content = ""
        images = []
        
        if detail:
            if isinstance(detail, dict):
                notes_list = detail.get("notes", [])
                if notes_list:
                    first_note = notes_list[0]
                    content = first_note.get("desc", "")  # 注意：字段名是desc而不是content
                    image_list = first_note.get("imageList", [])  # 注意：字段名是imageList而不是images
                    # 提取图片URL
                    for img in image_list:
                        # 从infoList或urlDefault获取图片URL
                        if "infoList" in img and img["infoList"]:
                            # 使用infoList中的第一个URL
                            images.append({"url": img["infoList"][0].get("url", "")})
                        elif "urlDefault" in img:
                            # 使用urlDefault
                            images.append({"url": img["urlDefault"]})
        
        print(f"📝 帖子内容长度: {len(content)} 字符")
        print(f"🖼️ 图片数量: {len(images)}")
        
        # 获取总结
        summary = summaries.get(title, "")
        if summary:
            summary_count += 1
            print(f"📋 包含总结，长度: {len(summary)} 字符")
        else:
            print(f"⚠️ 无总结内容")
        
        # 生成图片HTML
        images_html = ""
        for img in images:
            img_url = img.get("url", "")
            if img_url:
                images_html += f"<img src='{img_url}' alt='帖子图片' style='width: 100%; height: auto; border-radius: 4px; margin: 5px;'>"
        
        # 生成单个帖子HTML - 使用简单的字符串拼接
        post_html = ""
        post_html += f"<div style='background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); margin-bottom: 30px; padding: 20px; transition: transform 0.3s ease, box-shadow 0.3s ease;'>"
        post_html += f"<div>"
        post_html += f"<h2 style='font-size: 24px; color: #2c3e50; margin-bottom: 10px;'><a href='{note_url}' target='_blank' style='color: #2c3e50; text-decoration: none;'>{i+1}. {title}</a></h2>"
        post_html += f"<div style='display: flex; align-items: center; color: #7f8c8d; font-size: 14px;'>"
        post_html += f"<div style='display: flex; align-items: center; margin-right: 20px;'>"
        post_html += f"<img src='{user.get('avatar', '')}' alt='用户头像' style='width: 30px; height: 30px; border-radius: 50%; margin-right: 10px;'>"
        post_html += f"<span style='font-weight: 500; margin-right: 10px;'>{user.get('nickname', '匿名用户')}</span>"
        post_html += f"</div>"
        post_html += f"<div style='display: flex; gap: 20px;'>"
        post_html += f"<div style='display: flex; align-items: center; gap: 5px;'>👍 {interact_info.get('liked_count', 0)}</div>"
        post_html += f"<div style='display: flex; align-items: center; gap: 5px;'>💾 {interact_info.get('collected_count', 0)}</div>"
        post_html += f"<div style='display: flex; align-items: center; gap: 5px;'>💬 {interact_info.get('comment_count', 0)}</div>"
        post_html += f"<div style='display: flex; align-items: center; gap: 5px;'>🔗 {interact_info.get('share_count', 0)}</div>"
        post_html += f"</div>"
        post_html += f"</div>"
        post_html += f"</div>"
        
        if content:
            post_html += f"<div style='margin: 20px 0; line-height: 1.8; color: #555;'>{content}</div>"
        
        if images_html:
            post_html += f"<div style='margin: 20px 0;'>{images_html}</div>"
        
        if summary:
            post_html += f"<div style='background-color: #e8f4f8; border-left: 4px solid #3498db; padding: 15px; margin: 20px 0; border-radius: 4px;'>"
            post_html += f"<h3 style='color: #2c3e50; margin-bottom: 10px;'>📝 内容总结</h3>"
            post_html += f"<div style='line-height: 1.6; color: #333;'>{summary}</div>"
            post_html += f"</div>"
        
        post_html += f"</div>"
        
        posts_html += post_html
        processed_count += 1
        print(f"✅ 第 {i+1} 篇帖子处理完成")
    
    print(f"📋 帖子处理完成，共处理 {processed_count} 篇，其中 {summary_count} 篇包含总结")
    
    # 生成完整HTML
    print(f"🔨 开始生成完整的HTML内容")
    html_content = f"<!DOCTYPE html>\n"
    html_content += f"<html lang='zh-CN'>\n"
    html_content += f"<head>\n"
    html_content += f"<meta charset='UTF-8'>\n"
    html_content += f"<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
    html_content += f"<title>大模型面试经验分享 - 带总结</title>\n"
    html_content += f"<style>\n"
    html_content += f"* {{ margin: 0; padding: 0; box-sizing: border-box; }}\n"
    html_content += f"body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5; }}\n"
    html_content += f".container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}\n"
    html_content += f"h1 {{ text-align: center; color: #2c3e50; margin-bottom: 30px; padding: 20px 0; border-bottom: 2px solid #3498db; }}\n"
    html_content += f".footer {{ text-align: center; color: #7f8c8d; padding: 20px 0; margin-top: 50px; border-top: 1px solid #e0e0e0; }}\n"
    html_content += f"</style>\n"
    html_content += f"</head>\n"
    html_content += f"<body>\n"
    html_content += f"<div class='container'>\n"
    html_content += f"<h1>大模型面试经验分享 - 带内容总结</h1>\n"
    html_content += f"<!-- 帖子列表 -->\n"
    html_content += f"{posts_html}\n"
    html_content += f"<div class='footer'>\n"
    html_content += f"<p>生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>\n"
    html_content += f"<p>共 {len(posts)} 篇帖子</p>\n"
    html_content += f"</div>\n"
    html_content += f"</div>\n"
    html_content += f"</body>\n"
    html_content += f"</html>\n"
    
    print(f"📄 HTML内容生成完成，总长度: {len(html_content)} 字符")
    
    # 保存HTML文件
    print(f"💾 开始保存HTML文件: {HTML_FILE}")
    try:
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"✅ HTML网页已成功生成: {HTML_FILE}")
        print(f"📊 共生成 {processed_count} 篇帖子，其中 {summary_count} 篇包含总结")
    except Exception as e:
        print(f"❌ 保存HTML文件失败: {e}")
        raise

def main():
    """
    主函数
    """
    print("🚀 启动帖子总结程序")
    start_time = time.time()
    
    # 确保输出目录存在
    ensure_output_dirs()
    
    # 1. 加载帖子详情
    posts = load_post_details()
    if not posts:
        print("❌ 没有找到帖子详情")
        return
    
    print(f"✅ 加载了 {len(posts)} 篇帖子详情")
    
    # 2. 对每个帖子进行总结和判断
    valid_posts = []  # 保存符合条件的帖子
    summaries = {}
    print(f"📝 开始对帖子进行总结")
    
    for i, post_item in enumerate(posts):
        print(f"🔧 正在处理第 {i+1}/{len(posts)} 篇帖子")
        post = post_item.get("data", {})
        basic_info = post.get("basic_info", {})
        detail = post.get("detail", {})
        filename = post_item.get("filename", "")
        
        title = basic_info.get("title", "无标题")
        
        # 提取内容和图片
        content = ""
        images = []
        if detail:
            if isinstance(detail, dict):
                notes_list = detail.get("notes", [])
                if notes_list:
                    first_note = notes_list[0]
                    content = first_note.get("desc", "")  # 注意：字段名是desc而不是content
                    
                    # 提取图片URL
                    image_list = first_note.get("imageList", [])  # 注意：字段名是imageList而不是images
                    for img in image_list:
                        img_url = ""
                        if "infoList" in img and img["infoList"]:
                            # 使用infoList中的第一个URL
                            img_url = img["infoList"][0].get("url", "")
                        elif "urlDefault" in img:
                            # 使用urlDefault
                            img_url = img["urlDefault"]
                        elif "url" in img:
                            # 使用url字段
                            img_url = img["url"]
                        
                        if img_url:
                            images.append({"url": img_url})
        
        # 合并内容用于判断
        combined_content = content
        for img in images:
            combined_content += f"\n图片URL: {img.get('url', '')}"
        
        if combined_content:
            print(f"📄 帖子标题: '{title[:30]}...'")
            print(f"📝 内容长度: {len(combined_content)} 字符")
            print(f"📸 图片数量: {len(images)} 张")
            
            # 直接判断是否为大模型相关面试题，不需要先总结
            is_llm_interview = is_llm_interview_question(combined_content)
            print(f"📋 是大模型相关面试题: {is_llm_interview}")
            
            if is_llm_interview:
                # 只有符合条件的帖子才进行总结
                summary = summarize_content(content, title, images)
                if summary:
                    summaries[title] = summary
                    save_summary(title, summary)
                    valid_posts.append(post_item)  # 只保留符合条件的帖子
                    print(f"✅ 帖子符合条件，已添加到有效列表")
                else:
                    print(f"❌ 总结失败，跳过此帖子")
            else:
                print(f"❌ 帖子不符合条件，准备删除")
                # 删除不符合条件的帖子详情文件
                detail_file_path = os.path.join(DETAIL_DIR, filename)
                if os.path.exists(detail_file_path):
                    os.remove(detail_file_path)
                    print(f"✅ 已删除不符合条件的帖子文件: {detail_file_path}")
        else:
            print(f"⚠️  帖子内容为空，准备删除")
            # 删除内容为空的帖子详情文件
            detail_file_path = os.path.join(DETAIL_DIR, filename)
            if os.path.exists(detail_file_path):
                os.remove(detail_file_path)
                print(f"✅ 已删除内容为空的帖子文件: {detail_file_path}")
        
        # 避免请求过快
        time.sleep(2)
    
    print(f"✅ 已总结 {len(summaries)} 篇符合条件的帖子")
    
    # 3. 生成包含总结的HTML网页
    if valid_posts:
        print(f"📝 开始生成包含总结的HTML网页")
        generate_html_with_summary(valid_posts, summaries)
    else:
        print(f"⚠️  没有符合条件的帖子，跳过HTML生成")
    
    # 保存OCR缓存
    save_ocr_cache()
    
    end_time = time.time()
    print(f"🎉 帖子总结完成！耗时: {end_time - start_time:.2f} 秒")
    print(f"📁 总结保存目录: {os.path.abspath(SUMMARY_DIR)}")
    if valid_posts:
        print(f"🌐 包含总结的HTML网页: {os.path.abspath(HTML_FILE)}")
    print(f"📊 共处理 {len(posts)} 篇帖子，其中 {len(valid_posts)} 篇符合大模型相关面试题条件")

if __name__ == "__main__":
    main()