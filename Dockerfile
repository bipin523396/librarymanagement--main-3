# Dockerfile for Vercel (Django app)
# -------------------------------------------------
# 1. Base image – Python 3.9 (slim)
FROM python:3.9-slim

# 2. Set working directory to /app
WORKDIR /app

# 3. Install system build tools (gcc, libpq-dev etc.)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements and install Python dependencies
COPY project_code/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the entire project
COPY . .

# 6. Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=bookhub_backend.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/project_code

# 7. Collect static files (optional)
WORKDIR /app/project_code
RUN python manage.py collectstatic --noinput || true

# 8. Expose port Vercel expects for containers
EXPOSE 8080

# 9. Run the app with Gunicorn
CMD ["gunicorn", "bookhub_backend.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "2"]
