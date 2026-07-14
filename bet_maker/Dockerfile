FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config/ ./config/
COPY bet_maker/ ./bet_maker/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "bet_maker.main:app", "--host", "0.0.0.0", "--port", "8000"]
