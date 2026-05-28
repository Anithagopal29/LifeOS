#!/usr/bin/env bash
# build.sh — Render build step for LifeOS
# Exit on any error so a failed build doesn't deploy a broken app.
set -o errexit

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Collect static files into STATIC_ROOT (served by WhiteNoise)
python manage.py collectstatic --no-input

# 3. Apply database migrations
python manage.py migrate

# 4. Seed default categories (idempotent — safe to run on every deploy)
python manage.py seed_data
