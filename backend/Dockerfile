FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
# Copia Docs para /Docs (espelha a estrutura local — prompts.py usa parents[3]/Docs)
COPY Docs /Docs

EXPOSE 8000

# SQLite: use 1 worker; database file lives on mounted /data volume
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
