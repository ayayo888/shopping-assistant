# syntax=docker/dockerfile:1
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy and install dependencies
COPY backend/requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application source
COPY backend ./backend
COPY openapi.yml ./

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"] 