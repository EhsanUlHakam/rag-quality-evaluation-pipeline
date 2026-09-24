FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/service

WORKDIR /app

COPY service/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY service /app/service
COPY knowledge-base /app/knowledge-base
COPY evaluation-data /app/evaluation-data
COPY config /app/config

RUN mkdir -p /app/data /app/reports

EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
