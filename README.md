# 小红书大模型面试经验分享爬虫

## 项目简介

这是一个用于爬取小红书上关于大模型面试经验分享的爬虫项目，主要功能包括：

1. 搜索小红书上关于大模型面试的帖子
2. 获取帖子的详细内容
3. 对帖子中的图片进行OCR识别
4. 生成HTML网页展示所有帖子
5. 清理JSON文件中的敏感信息

## 远程服务器配置

### 服务器连接信息

| 项目 | 值 |
|------|-----|
| 服务器地址 | 34.29.5.105 |
| 用户名 | milk |
| SSH密钥 | ~/.ssh/milk |
| 远程项目目录 | /root/python-okx/python-okx |

连接命令：
```bash
ssh -i ~/.ssh/milk milk@34.29.5.105
```

### 数据库配置

| 项目 | 值 |
|------|-----|
| 数据库类型 | MySQL |
| 密码 | !A33b3e561fec |

### 数据同步方式

1. 本地开发完成后，通过GitHub同步代码到远程服务器
2. 远程服务器密码修改需要直接连接服务器进行修改
3. 同步命令（在远程服务器执行）：
   ```bash
   cd /root/python-okx/python-okx
   git pull origin main
   ```

## 本地开发环境

### Python环境

项目使用虚拟环境进行依赖管理：

| 环境 | Python版本 | 路径 |
|------|-----------|------|
| 主环境 | 3.9 | /Volumes/600g/app1/okx-py/bin/python |
| 辅助环境 | 3.13.2 | /Users/aaa/python-sdk/python3.13.2/bin/python |

### 快速启动

```bash
# 使用主Python环境运行示例
/Volumes/600g/app1/okx-py/bin/python3 example.py
```

## GitHub仓库

- 仓库地址：https://github.com/likecu
- 代码同步：本地提交后推送到GitHub，远程服务器从GitHub拉取更新

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

## 常用搜索接口

### 默认搜索配置

项目的搜索配置文件为 `search_config.json`，当前配置包含以下搜索关键词：

| 分类 | 搜索关键词 | 用途 |
|------|-----------|------|
| 面试经验 | 大模型面试 经验分享 | 获取大模型面试经验分享 |
| 面试技巧 | 大模型面试技巧 | 获取大模型面试技巧 |

### 常用搜索关键词列表

#### 1. 刷题相关
| 搜索关键词 | 说明 |
|-----------|------|
| leetcode 刷题 | LeetCode刷题经验 |
| 算法刷题 | 算法刷题技巧 |
| 刷题路线 | 刷题学习路线 |
| 刷题顺序 | 刷题顺序建议 |
| 题目分类 | 题目分类整理 |

#### 2. 面试相关
| 搜索关键词 | 说明 |
|-----------|------|
| 面试经验 | 面试经验分享 |
| 面试题 | 面试题目汇总 |
| 面试技巧 | 面试技巧总结 |
| 面试准备 | 面试准备攻略 |
| 算法面试 | 算法面试题目 |
| 编程面试 | 编程面试经验 |

#### 3. 大模型相关
| 搜索关键词 | 说明 |
|-----------|------|
| 大模型面试 | 大模型岗位面试 |
| LLM面试 | 大语言模型面试 |
| AI面试 | AI岗位面试 |
| 机器学习面试 | 机器学习面试 |
| 深度学习面试 | 深度学习面试 |

#### 4. 触发更新关键词
| 搜索关键词 | 说明 |
|-----------|------|
| 更新 | 获取最新内容 |
| 2024 | 获取2024年内容 |
| 2025 | 获取2025年内容 |
| 最新 | 获取最新分享 |
| 总结 | 获取总结类内容 |

### 自定义搜索配置

修改 `search_config.json` 文件来自定义搜索：

```json
{
  "search_terms": [
    "大模型面试 经验分享",
    "大模型面试技巧",
    "leetcode 刷题",
    "算法面试",
    "面试经验"
  ],
  "page_num": 2,
  "page_size": 20
}
```

### 搜索参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| search_terms | 搜索关键词列表 | - |
| page_num | 爬取页数 | 2 |
| page_size | 每页数量 | 20 |

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

## 远程部署

### 1. 连接到远程服务器

```bash
ssh -i ~/.ssh/milk milk@34.29.5.105
```

### 2. 同步代码

在本地开发完成后，推送代码到GitHub，然后在远程服务器上拉取：

```bash
# 远程服务器上执行
cd /root/python-okx/python-okx
git pull origin main
```

### 3. 部署MCP服务

```bash
# 检查media-crawler-mcp-service目录
cd /root/python-okx/python-okx/media-crawler-mcp-service

# 启动MCP服务
docker compose up -d

# 验证服务状态
docker compose ps
```

### 4. 远程服务器上运行爬虫

```bash
# 安装依赖
cd /root/python-okx/python-okx
pip install -r requirements.txt

# 运行爬虫
python3 -m xhs_crawler.crawlers.xhs_interview_crawler

# 清理敏感信息
python3 -m xhs_crawler.cleaners.clean_json_files

# 生成HTML
python3 -m xhs_crawler.generators.generate_complete_html
```

### 5. 小红书登录配置

详细登录方式请参考 [小红书登录指南](./小红书登录指南.md)

支持的登录方式：
- 管理界面登录
- API登录（二维码/Cookie）

### 6. 验证部署

- 检查MCP服务是否正常运行
- 测试爬虫功能是否正常
- 验证生成的HTML页面是否可访问

## 常用命令速查

### 本地开发

```bash
# 运行示例
/Volumes/600g/app1/okx-py/bin/python3 example.py

# 运行爬虫（使用主环境）
/Volumes/600g/app1/okx-py/bin/python3 -m xhs_crawler.crawlers.xhs_interview_crawler

# 运行爬虫（使用辅助环境）
/Users/aaa/python-sdk/python3.13.2/bin/python3 -m xhs_crawler.crawlers.xhs_interview_crawler
```

### 远程服务器

```bash
# SSH连接
ssh -i ~/.ssh/milk milk@34.29.5.105

# Git同步
cd /root/python-okx/python-okx && git pull origin main

# MCP服务管理
cd /root/python-okx/python-okx/media-crawler-mcp-service
docker compose up -d    # 启动
docker compose down     # 停止
docker compose ps       # 查看状态
docker compose logs -f  # 查看日志
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
