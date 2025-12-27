#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细测试搜索工具超时问题
"""
import requests
import json
import time
import socket
import urllib3

# 启用详细日志
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_socket_connection(host, port, timeout=10):
    """
    测试TCP套接字连接
    """
    print(f"\n=== 测试TCP套接字连接到 {host}:{port} ===")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start_time = time.time()
        result = sock.connect_ex((host, port))
        elapsed_time = time.time() - start_time
        
        if result == 0:
            print(f"✓ 连接成功！耗时: {elapsed_time:.2f}秒")
        else:
            print(f"✗ 连接失败，错误码: {result}")
        
        sock.close()
        return result == 0
        
    except Exception as e:
        print(f"✗ 连接异常: {type(e).__name__}: {e}")
        return False

def test_http_request(host, port, path, method="GET", data=None, headers=None, timeout=30):
    """
    详细测试HTTP请求
    """
    url = f"http://{host}:{port}{path}"
    print(f"\n=== 测试HTTP请求到 {url} ===")
    print(f"方法: {method}")
    print(f"超时: {timeout}秒")
    
    if headers:
        print(f"请求头: {json.dumps(headers, ensure_ascii=False)}")
    
    if data:
        print(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        session = requests.Session()
        
        # 配置详细日志
        session.verify = False
        
        request_start = time.time()
        
        if method == "GET":
            response = session.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            response = session.post(url, json=data, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
        
        request_end = time.time()
        
        print(f"请求耗时: {request_end - request_start:.2f}秒")
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {json.dumps(dict(response.headers), ensure_ascii=False)}")
        print(f"响应内容长度: {len(response.content)}字节")
        print(f"响应内容: {response.text[:500]}...")
        
        return response.status_code, response.text
        
    except requests.exceptions.ConnectTimeout:
        print(f"✗ 连接超时！服务器可能无法响应或网络延迟过高")
        return None, "连接超时"
    
    except requests.exceptions.ReadTimeout:
        print(f"✗ 读取超时！服务器连接成功但未在指定时间内返回数据")
        return None, "读取超时"
    
    except requests.exceptions.ConnectionError as e:
        print(f"✗ 连接错误: {e}")
        return None, f"连接错误: {str(e)}"
    
    except Exception as e:
        print(f"✗ 其他异常: {type(e).__name__}: {e}")
        return None, f"其他异常: {str(e)}"

if __name__ == "__main__":
    host = "34.29.5.105"
    port = 9091
    
    print("开始详细测试搜索工具超时问题...")
    
    # 1. 测试TCP连接
    test_socket_connection(host, port)
    
    # 2. 测试系统状态API（简单请求，验证基本连接）
    test_http_request(host, port, "/api/status/system", method="GET", timeout=10)
    
    # 3. 测试登录状态API（验证业务逻辑）
    test_http_request(host, port, "/api/login/status/xhs", method="GET", timeout=10)
    
    # 4. 测试搜索工具API（问题所在）
    headers = {"Content-Type": "application/json"}
    data = {
        "tool": "xhs_search",
        "params": {
            "keywords": "大模型",
            "page_num": 1,
            "page_size": 1
        }
    }
    
    # 先测试一个简化版的搜索请求
    test_http_request(host, port, "/api/admin/inspector/execute", method="POST", 
                     data=data, headers=headers, timeout=30)
    
    print("\n=== 测试完成 ===")
