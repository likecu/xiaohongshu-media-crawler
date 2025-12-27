# 使用Python 3.9作为基础镜像，并指定为linux/amd64架构
FROM --platform=linux/amd64 python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --upgrade pip && pip install -r requirements.txt

# 复制整个项目到工作目录
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app

# 定义容器启动命令
CMD ["python", "example.py"]