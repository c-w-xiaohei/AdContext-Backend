FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt pyproject.toml ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "gateway/main.py", "--host", "0.0.0.0", "--port", "8080"]