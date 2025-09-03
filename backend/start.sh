#!/bin/bash
# Render deployment start script for AI Fashion Backend

echo "🚀 Starting AI Fashion Backend on Render..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src/backend/prods_fastapi"

# Change to the FastAPI directory
cd /opt/render/project/src/backend/prods_fastapi

# Install requirements if requirements-render.txt exists, otherwise use requirements.txt
if [ -f "requirements-render.txt" ]; then
    echo "📦 Installing Render-optimized dependencies..."
    pip install -r requirements-render.txt
elif [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "❌ No requirements file found!"
    exit 1
fi

# Initialize database tables if needed
echo "🗄️ Initializing database..."
python -c "
try:
    from database import create_tables, init_color_palette_data
    create_tables()
    init_color_palette_data()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'⚠️ Database initialization warning: {e}')
"

# Start the FastAPI application
echo "🌟 Starting FastAPI server..."
exec python main.py
