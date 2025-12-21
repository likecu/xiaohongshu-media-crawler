# 小红书大模型面试经验分享爬虫

## 项目简介

这是一个用于爬取小红书上关于大模型面试经验分享的爬虫项目，主要功能包括：

1. 搜索小红书上关于大模型面试的帖子
2. 获取帖子的详细内容
3. 对帖子中的图片进行OCR识别
4. 生成HTML网页展示所有帖子
5. 清理JSON文件中的敏感信息

## 项目结构

```
.
├── xhs_crawler/             # 爬虫主目录
│   ├── cleaners/            # 清理工具
│   │   ├── __init__.py
│   │   └── clean_json_files.py      # 清理JSON文件中的敏感字段
│   ├── core/                # 核心模块
│   │   ├── __init__.py
│   │   ├── base_crawler.py          # 爬虫基类
│   │   ├── config.py                # 配置文件
│   │   └── mcp_utils.py             # MCP工具调用和公共函数
│   ├── crawlers/            # 爬虫实现
│   │   ├── __init__.py
│   │   ├── multi_keyword_crawler.py # 多关键词爬虫实现
│   │   ├── simple_xhs_crawler.py    # 简单爬虫实现
│   │   └── xhs_interview_crawler.py # 面试经验爬虫实现
│   ├── generators/          # HTML生成工具
│   │   ├── __init__.py
│   │   ├── generate_complete_html.py # 生成完整HTML
│   │   ├── generate_html_from_existing.py # 从现有数据生成HTML
│   │   └── html_generator.py        # HTML生成工具
│   └── summarizers/         # 帖子总结
│       ├── __init__.py
│       └── summarize_posts.py       # 帖子总结
├── .gitignore               # Git忽略文件
├── README.md                # 项目说明文档
├── get_hotel_reviews        # 酒店评论获取脚本
├── start_mcp_service.sh     # 启动MCP服务脚本
├── stop_mcp_service.sh      # 停止MCP服务脚本
└── 小红书登录指南.md          # 小红书登录指南
```

## 模块说明

### 1. 公共模块
- **mcp_utils.py**: 提供MCP工具调用、目录管理、JSON数据保存和加载等公共功能
- **html_generator.py**: 负责生成HTML网页，包括单个帖子HTML和完整HTML页面
- **base_crawler.py**: 爬虫基类，包含所有爬虫的共同逻辑，如搜索帖子、获取详情等

### 2. 爬虫实现
- **simple_xhs_crawler.py**: 简单爬虫，使用单个关键词搜索帖子
- **multi_keyword_crawler.py**: 多关键词爬虫，支持多个关键词和多页爬取
- **xhs_interview_crawler.py**: 面试经验爬虫，从配置文件读取搜索词，支持OCR识别

### 3. 工具脚本
- **clean_json_files.py**: 清理JSON文件中的敏感字段，如token、密钥等
- **generate_complete_html.py**: 生成完整的HTML页面
- **generate_html_from_existing.py**: 从现有数据生成HTML页面
- **summarize_posts.py**: 对帖子进行总结

## 配置文件

- **search_config.json**: 配置搜索关键词、页码和每页数量
- **mcp-config.json**: 配置MCP服务的端点和参数
- **xhs_tools.json**: 配置小红书工具的参数
- **clean_config.json**: 配置JSON清理器的敏感字段列表

## 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行爬虫

```bash
# 运行简单爬虫
python3 -m xhs_crawler.crawlers.simple_xhs_crawler

# 运行多关键词爬虫
python3 -m xhs_crawler.crawlers.multi_keyword_crawler

# 运行面试经验爬虫
python3 -m xhs_crawler.crawlers.xhs_interview_crawler
```

### 3. 清理JSON文件

```bash
# 清理当前目录下的所有JSON文件
python3 -m xhs_crawler.cleaners.clean_json_files

# 清理指定目录下的所有JSON文件
python3 -m xhs_crawler.cleaners.clean_json_files /path/to/directory

# 使用自定义敏感字段列表清理JSON文件
python3 -m xhs_crawler.cleaners.clean_json_files /path/to/directory field1,field2
```

### 4. 生成HTML页面

```bash
# 生成完整HTML
python3 -m xhs_crawler.generators.generate_complete_html

# 从现有数据生成HTML
python3 -m xhs_crawler.generators.generate_html_from_existing
```

### 5. 帖子总结

```bash
# 运行帖子总结脚本
python3 -m xhs_crawler.summarizers.summarize_posts
```

## 隐私保护

- 项目使用`.gitignore`文件确保敏感文件不被提交到GitHub
- `clean_json_files.py`脚本可以清理JSON文件中的敏感字段
- 支持从配置文件加载敏感字段列表，方便自定义
- 所有API密钥和令牌都不会硬编码在代码中

## 开发规范

- 代码使用Python 3.8+语法
- 遵循PEP 8编码规范
- 使用类型注解
- 添加函数级注释，包括参数、返回值和异常
- 模块化设计，便于扩展和维护

## 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提交Issue或Pull Request。
