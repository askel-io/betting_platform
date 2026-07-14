FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config/ ./config/
COPY line_provider/ ./line_provider/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "line_provider.main:app", "--host", "0.0.0.0", "--port", "8000"]
