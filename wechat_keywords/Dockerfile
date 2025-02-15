# 使用官方 Python 镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制整个项目代码到容器
COPY . .

# 使用阿里云镜像源安装依赖
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt

# 设置环境变量 PYTHONPATH，确保模块可以被正确找到
ENV PYTHONPATH=/app

# 设置 PYTHONUNBUFFERED 环境变量，确保 Python 输出实时显示
ENV PYTHONUNBUFFERED=1

# 设置ENTRYPOINT
ENTRYPOINT ["python", "-m", "data_processor"]

# 设置默认参数（可以在运行时覆盖）
CMD ["--base_path", "/data", "--csv_file_name", "article_list.csv", "--api_type", "ollama", "--api_url", "http://127.0.0.1:11434", "--api_key", "NONE", "--llm_model","qwen2.5:7b"]