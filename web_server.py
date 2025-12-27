#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的HTTP服务器，用于展示爬虫生成的HTML文件和结果
"""

import http.server
import socketserver
import os
import sys
import threading
import time

def run_web_server():
    """
    启动HTTP服务器
    """
    # 设置服务器端口
    PORT = 8000
    
    # 设置工作目录为当前目录
    os.chdir('/app')
    
    # 创建HTTP服务器
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
            print(f"\n🌐 Web服务器已启动，端口: {PORT}")
            print(f"📁 服务目录: /app")
            print(f"🔗 访问地址: http://0.0.0.0:{PORT}")
            # print(f"💡 可以通过 http://<外部IP>:{PORT} 从外部访问")
            print("=" * 60)
            
            # 启动服务器，直到被中断
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Web服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动Web服务器失败: {e}")

def main():
    """
    主函数，先运行爬虫，再启动Web服务器
    """
    # 导入爬虫主模块
    try:
        import example
        
        # 运行爬虫
        print("🎯 开始运行小红书爬虫...")
        example.main()
        print("✅ 爬虫运行完成")
    except Exception as e:
        print(f"❌ 运行爬虫时出错: {e}")
    
    # 启动Web服务器
    print("\n📦 准备启动Web服务器...")
    run_web_server()

if __name__ == "__main__":
    main()