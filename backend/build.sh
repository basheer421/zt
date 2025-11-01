#!/usr/bin/env bash
# Render build script for ZT-Verify backend

set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from database import init_db; init_db()"

# Create demo users
python create_demo_users.py

echo "Build complete!"
