# 使用 Python 3.12 官方映像
FROM python:3.12-slim

# 設定工作目錄
WORKDIR /app

# 安裝 uv 套件管理工具
RUN pip install --no-cache-dir uv

# 複製專案依賴檔案
COPY pyproject.toml uv.lock ./

# 建立虛擬環境並安裝依賴
RUN uv venv && \
    uv sync --frozen

# 複製應用程式碼
COPY . .

# 暴露 FastAPI 預設端口
EXPOSE 8000

# 使用 uv 執行 uvicorn
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
