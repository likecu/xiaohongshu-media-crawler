#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理JSON文件中的敏感字段

功能: 递归遍历指定目录下的所有JSON文件，删除指定的敏感字段
参数:
    - 命令行参数1: 目录路径，默认当前目录
    - 命令行参数2: 要删除的字段，默认 xsec_token, xsec_source

使用示例:
    python clean_json_files.py /path/to/directory
    python clean_json_files.py /path/to/directory field1,field2
"""

import os
import json
import sys
import re
from typing import List, Dict, Any, Set, Tuple


# 默认敏感字段列表
DEFAULT_SENSITIVE_FIELDS = [
    "xsec_token",
    "xsec_source",
    "cookie",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "api_key",
    "api_secret",
    "password",
    "passwd",
    "auth",
    "authorization",
    "session",
    "session_id",
    "session_key",
    "csrf_token",
    "uid",
    "user_id",
    "user_token",
    "secret_key",
    "private_key",
    "public_key",
    "key_id",
    "app_id",
    "app_secret"
]


class JsonCleaner:
    """
    JSON文件清理器，用于删除敏感字段
    """
    
    def __init__(self, fields_to_remove: List[str] = None):
        """
        初始化JSON清理器
        
        Args:
            fields_to_remove: 要删除的字段列表
        """
        if fields_to_remove:
            self.fields_to_remove = fields_to_remove
        else:
            self.fields_to_remove = DEFAULT_SENSITIVE_FIELDS
        
        self.total_files = 0
        self.cleaned_files = 0
        self.total_fields_removed = 0
    
    def clean_json_file(self, file_path: str) -> None:
        """
        清理单个JSON文件中的敏感字段
        
        Args:
            file_path: JSON文件路径
        """
        self.total_files += 1
        
        try:
            # 尝试使用UTF-8编码打开文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 递归删除敏感字段
            fields_removed = 0
            
            def remove_fields(obj: Any) -> Tuple[Any, int]:
                nonlocal fields_removed
                
                if isinstance(obj, dict):
                    # 删除当前字典中的敏感字段
                    for field in self.fields_to_remove:
                        if field in obj:
                            del obj[field]
                            fields_removed += 1
                    # 递归处理子字典
                    for key, value in obj.items():
                        obj[key], _ = remove_fields(value)
                elif isinstance(obj, list):
                    # 递归处理列表中的每个元素
                    for i, item in enumerate(obj):
                        obj[i], _ = remove_fields(item)
                return obj, fields_removed
            
            cleaned_data, fields_removed = remove_fields(data)
            
            # 如果有字段被删除，才保存文件
            if fields_removed > 0:
                # 保存清理后的文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
                
                print(f"✓ 已清理: {file_path} (删除 {fields_removed} 个敏感字段)")
                self.cleaned_files += 1
                self.total_fields_removed += fields_removed
            else:
                print(f"➤ 无需清理: {file_path} (未发现敏感字段)")
            
        except UnicodeDecodeError as e:
            # 跳过非UTF-8编码的文件
            print(f"✗ 编码错误 {file_path}: {e}")
        except json.JSONDecodeError as e:
            print(f"✗ JSON错误 {file_path}: {e}")
        except IOError as e:
            print(f"✗ IO错误 {file_path}: {e}")
        except Exception as e:
            # 捕获其他所有异常，继续处理下一个文件
            print(f"✗ 未知错误 {file_path}: {e}")
    
    def clean_json_files_in_directory(self, directory: str) -> None:
        """
        递归清理目录下的所有JSON文件
        
        Args:
            directory: 要清理的目录路径
        """
        # 递归遍历目录
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    self.clean_json_file(file_path)
    
    def get_statistics(self) -> Dict[str, int]:
        """
        获取清理统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "total_files": self.total_files,
            "cleaned_files": self.cleaned_files,
            "total_fields_removed": self.total_fields_removed,
            "fields_to_remove": len(self.fields_to_remove)
        }
    
    def print_statistics(self) -> None:
        """
        打印清理统计信息
        """
        stats = self.get_statistics()
        print("\n=" * 50)
        print("清理统计信息：")
        print(f"总文件数: {stats['total_files']}")
        print(f"已清理文件数: {stats['cleaned_files']}")
        print(f"删除的敏感字段总数: {stats['total_fields_removed']}")
        print(f"使用的敏感字段列表长度: {stats['fields_to_remove']}")
        print("=" * 50)


def load_config(config_file: str = "clean_config.json") -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置字典
    """
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"⚠️ 加载配置文件失败: {config_file}, {e}")
            return {}
    return {}


def main():
    """
    主函数，处理命令行参数并执行清理操作
    """
    # 加载配置文件
    config = load_config()
    
    # 默认参数
    directory = "."
    fields_to_remove = DEFAULT_SENSITIVE_FIELDS
    
    # 从配置文件获取参数
    if config:
        config_fields = config.get("fields_to_remove")
        if config_fields and isinstance(config_fields, list):
            fields_to_remove = config_fields
    
    # 处理命令行参数
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    
    if len(sys.argv) > 2:
        fields_to_remove = sys.argv[2].split(',')
    
    print(f"开始清理目录: {directory}")
    print(f"要删除的字段: {fields_to_remove}")
    print(f"字段数量: {len(fields_to_remove)}")
    print("=" * 50)
    
    # 创建清理器实例
    cleaner = JsonCleaner(fields_to_remove)
    
    # 执行清理操作
    cleaner.clean_json_files_in_directory(directory)
    
    # 打印统计信息
    cleaner.print_statistics()
    
    print("清理完成！")


if __name__ == "__main__":
    main()