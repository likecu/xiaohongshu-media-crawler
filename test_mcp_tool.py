#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MCP API端点
"""
import requests
import json
import time

def test_login_start():
    """
    测试登录启动端点
    """
    print("\n=== 测试登录启动端点 (/api/login/start) ===")
    url = "http://34.29.5.105:9091/api/login/start"
    headers = {"Content-Type": "application/json"}
    data = {
        "platform": "xhs",
        "login_type": "qrcode"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=30
        )
        elapsed_time = time.time() - start_time
        print(f"请求耗时: {elapsed_time:.2f}秒")
        print(f"响应状态码: {response.status_code}")
        
        # 获取响应内容
        response_text = response.text
        print(f"响应内容: {response_text}")
        
        return response.status_code, response_text
        
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {type(e).__name__}: {e}")
        return None, str(e)
    except Exception as e:
        print(f"其他异常: {type(e).__name__}: {e}")
        return None, str(e)

def test_login_status():
    """
    测试登录状态端点
    """
    print("\n=== 测试登录状态端点 (/api/login/status/xhs) ===")
    url = "http://34.29.5.105:9091/api/login/status/xhs"
    
    try:
        start_time = time.time()
        response = requests.get(
            url,
            timeout=30
        )
        elapsed_time = time.time() - start_time
        print(f"请求耗时: {elapsed_time:.2f}秒")
        print(f"响应状态码: {response.status_code}")
        
        # 获取响应内容
        response_text = response.text
        print(f"响应内容: {response_text}")
        
        return response.status_code, response_text
        
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {type(e).__name__}: {e}")
        return None, str(e)
    except Exception as e:
        print(f"其他异常: {type(e).__name__}: {e}")
        return None, str(e)

def test_system_status():
    """
    测试系统状态端点
    """
    print("\n=== 测试系统状态端点 (/api/status/system) ===")
    url = "http://34.29.5.105:9091/api/status/system"
    
    try:
        start_time = time.time()
        response = requests.get(
            url,
            timeout=30
        )
        elapsed_time = time.time() - start_time
        print(f"请求耗时: {elapsed_time:.2f}秒")
        print(f"响应状态码: {response.status_code}")
        
        # 获取响应内容
        response_text = response.text
        print(f"响应内容: {response_text}")
        
        return response.status_code, response_text
        
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {type(e).__name__}: {e}")
        return None, str(e)
    except Exception as e:
        print(f"其他异常: {type(e).__name__}: {e}")
        return None, str(e)

def test_xhs_search_tool():
    """
    测试小红书搜索工具
    """
    print("\n=== 测试小红书搜索工具 (/api/admin/inspector/execute) ===")
    url = "http://34.29.5.105:9091/api/admin/inspector/execute"
    headers = {"Content-Type": "application/json"}
    data = {
        "tool": "xhs_search",
        "params": {
            "keywords": "大模型",
            "page_num": 1,
            "page_size": 1
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=30
        )
        elapsed_time = time.time() - start_time
        print(f"请求耗时: {elapsed_time:.2f}秒")
        print(f"响应状态码: {response.status_code}")
        
        # 获取响应内容
        response_text = response.text
        print(f"响应内容长度: {len(response_text)}字节")
        print(f"响应内容: {response_text[:1000]}...")
        
        # 尝试解析JSON
        if response_text:
            try:
                response_json = json.loads(response_text)
                print("响应JSON解析成功")
                print(f"JSON结构: {json.dumps(list(response_json.keys()), ensure_ascii=False)}")
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
        
        return response.status_code, response_text
        
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {type(e).__name__}: {e}")
        return None, str(e)
    except Exception as e:
        print(f"其他异常: {type(e).__name__}: {e}")
        return None, str(e)

if __name__ == "__main__":
    print("开始测试API端点...")
    
    # 测试系统状态
    test_system_status()
    
    # 测试登录状态
    test_login_status()
    
    # 测试登录启动
    test_login_start()
    
    # 测试搜索工具
    test_xhs_search_tool()
    
    print("\n=== 测试完成 ===")
