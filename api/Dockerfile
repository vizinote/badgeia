FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data
VOLUME /data

EXPOSE 8080

ENV DATABASE_PATH=/data/leads.db
ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]
