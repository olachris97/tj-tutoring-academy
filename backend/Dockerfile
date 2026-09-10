FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 10000

CMD ["sh", "-c", "flask --app run.py db upgrade && exec gunicorn --workers 1 --bind 0.0.0.0:${PORT:-10000} run:app"]
