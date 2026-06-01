# Dockerfile for Render/Deployment
# -------------------------------------------------
# 1. Base image – Python 3.11 (slim)
FROM python:3.11-slim

# 2. Set working directory to /app
WORKDIR /app

# 3. Install system build tools
RUN apt-get update && apt-get install -y gcc python3-dev libpq-dev && rm -rf /var/lib/apt/lists/*

# 4. Copy root requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the entire project
COPY . .

# 6. Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=bookhub_backend.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/project_code
ENV ALLOWED_HOSTS=*
ENV DEBUG=True

# 7. Work in project directory where manage.py is
WORKDIR /app/project_code

# 8. Collect static files
RUN python manage.py collectstatic --noinput

# 9. Expose port (Render uses PORT env var, but we expose 8000 by default)
EXPOSE 8000

# 10. Run the app with Gunicorn
# Using the PYTHONPATH we set earlier
CMD ["gunicorn", "bookhub_backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
