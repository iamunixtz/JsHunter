#!/bin/bash

# JSNinja Web Application Startup Script

echo "🔥 Starting JSNinja - JavaScript Secret Scanner 🔥"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed"
    exit 1
fi

# Prompt for Flask secret key configuration
echo ""
echo "🔐 Flask Secret Key Configuration"
echo "================================="
echo "For security, you should set a custom secret key for your Flask application."
echo ""
read -p "Do you want to set a custom secret key? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter your custom secret key (or press Enter for random generation): " custom_key
    
    if [ -z "$custom_key" ]; then
        # Generate a random secret key
        custom_key=$(python3 -c "import secrets; print(secrets.token_hex(32))")
        echo "✅ Generated random secret key: $custom_key"
    fi
    
    export FLASK_SECRET_KEY="$custom_key"
    echo "✅ Custom secret key has been set!"
else
    echo "ℹ️  Using default secret key (not recommended for production)"
fi

echo ""

# Prompt for admin user credentials
echo "👤 Admin User Configuration"
echo "=========================="
echo "Set up the admin username and password for the JSNinja web interface."
echo "Default: username=jsninja, password=jsninja"
echo ""

read -p "Enter admin username (default: jsninja): " ADMIN_USERNAME
ADMIN_USERNAME=${ADMIN_USERNAME:-jsninja}
export JSNINJA_ADMIN_USERNAME="$ADMIN_USERNAME"

read -s -p "Enter admin password (default: jsninja): " ADMIN_PASSWORD
ADMIN_PASSWORD=${ADMIN_PASSWORD:-jsninja}
echo ""

# Hash the password using Python's werkzeug.security
HASHED_PASSWORD=$(python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('$ADMIN_PASSWORD'))")
export JSNINJA_ADMIN_PASSWORD_HASH="$HASHED_PASSWORD"
echo "✅ Admin credentials set for user: $ADMIN_USERNAME"
echo ""

# Install requirements
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"
echo ""

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ Database initialized successfully')
"

if [ $? -ne 0 ]; then
    echo "❌ Failed to initialize database"
    exit 1
fi

echo ""

# Display startup information
echo "🚀 Starting JSNinja web server..."
echo "================================="
echo ""
echo "🌐 Access URLs:"
echo "   Local:    http://localhost:5000"
echo "   Network:  http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "🔧 Features:"
echo "   ✓ Project Management"
echo "   ✓ URL/File/Code Scanning"
echo "   ✓ 200+ Secret Patterns"
echo "   ✓ Historical Data Storage"
echo "   ✓ Analytics Dashboard"
echo "   ✓ User Authentication & Rate Limiting"
echo "   ✓ Live JS Monitoring (Beta)"
echo "   ✓ API Endpoint Extraction"
echo "   ✓ Export Scan Results"
echo "   ✓ Discord/Telegram Notifications"
echo "   ✓ Backend Logs Viewer"
echo ""
echo "☕ Support the project: https://buymeacoffee.com/iamunixtz"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================="
echo ""

# Start the application
python3 app.py
