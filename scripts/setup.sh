#!/bin/bash
# Setup script for PostgreSQL checker

echo "🐱 Setting up PostgreSQL Checker Script"
echo "========================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed!"
    echo "Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found"

# Install requirements
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies!"
    exit 1
fi

# Make the script executable
chmod +x check_postgres.py

echo ""
echo "🚀 Setup complete! You can now run:"
echo "   python3 check_postgres.py"
echo ""
echo "💡 Make sure PostgreSQL is running first:"
echo "   cd ../database && docker compose up -d"