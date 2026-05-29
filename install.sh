#!/bin/bash
# CF-Orion Pro Installer

echo "🔍 Installing CF-Orion Pro..."

# Check for git
if ! command -v git &> /dev/null; then
    echo "📦 Installing git..."
    sudo apt update && sudo apt install git -y
fi

# Check for python3 and pip
if ! command -v python3 &> /dev/null; then
    echo "📦 Installing python3..."
    sudo apt install python3 python3-pip -y
fi

# Clone and install
echo "📥 Downloading project..."
git clone https://github.com/alirezani/cf-orion-pro.git
cd cf-orion-pro
pip3 install -r requirements.txt

echo "✅ Installation complete!"
echo "🚀 Run 'cd cf-orion-pro && python3 app.py' to start."