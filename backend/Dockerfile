FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app

EXPOSE 8000

# 默认使用 SQLite（容器内文件），生产建议通过 DATABASE_URL 切到 PostgreSQL
ENV DATABASE_URL=sqlite:////app/app.db

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

