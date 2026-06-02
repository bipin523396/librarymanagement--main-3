#!/usr/bin/env bash
set -o errexit

# Automatically detect if we are in repository root or project_code subdirectory
if [ -d "project_code" ] && [ -f "project_code/manage.py" ]; then
    echo "==> Building inside project_code subdirectory..."
    cd project_code
else
    echo "==> Building inside current directory..."
fi

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run collectstatic
python manage.py collectstatic --noinput

# Create / reset admin account (username=admin, password=admin123)
echo "==> Creating admin account..."
python manage.py create_simple_admin --username admin --password admin123 || true

echo "==> Build completed successfully!"
