FROM python:3.9

# 设置工作目录
WORKDIR /app

# 复制所有文件到工作目录
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置容器启动时运行 app.py
CMD ["python", "app.py"]
