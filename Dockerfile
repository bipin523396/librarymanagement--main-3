FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=bookhub_backend.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/project_code
ENV DEBUG=False

WORKDIR /app/project_code

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["sh", "-c", "gunicorn bookhub_backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 2 --timeout 120 --access-logfile - --error-logfile -"]
