#!/bin/bash
# Instagram Watcher - PM2 Setup Script
# Starts the Instagram watcher as a permanent background process

echo "=========================================="
echo "Instagram Watcher - PM2 Setup"
echo "=========================================="

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "❌ PM2 is not installed"
    echo ""
    echo "Install PM2 with:"
    echo "  npm install -g pm2"
    echo ""
    exit 1
fi

echo "✅ PM2 is installed"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed"
    exit 1
fi

echo "✅ Python is available"

# Check if watcher file exists
WATCHER_PATH="watchers/instagram_watcher.py"
if [ ! -f "$WATCHER_PATH" ]; then
    echo "❌ Instagram watcher not found at: $WATCHER_PATH"
    exit 1
fi

echo "✅ Instagram watcher found"

# Stop existing instance if running
echo ""
echo "Stopping any existing instagram_watcher process..."
pm2 stop instagram_watcher 2>/dev/null || true
pm2 delete instagram_watcher 2>/dev/null || true

# Start the watcher
echo ""
echo "Starting Instagram watcher with PM2..."
pm2 start "$WATCHER_PATH" \
    --name instagram_watcher \
    --interpreter python \
    --max-memory-restart 500M \
    --restart-delay 3000 \
    --exp-backoff-restart-delay 100

# Save PM2 configuration
echo ""
echo "Saving PM2 configuration..."
pm2 save

# Setup PM2 startup (so it survives reboot)
echo ""
echo "Setting up PM2 startup script..."
pm2 startup

echo ""
echo "=========================================="
echo "✅ Instagram Watcher Started Successfully"
echo "=========================================="
echo ""
echo "Useful PM2 Commands:"
echo ""
echo "  View logs:        pm2 logs instagram_watcher"
echo "  View status:      pm2 status"
echo "  Restart:          pm2 restart instagram_watcher"
echo "  Stop:             pm2 stop instagram_watcher"
echo "  Monitor:          pm2 monit"
echo ""
echo "The watcher will:"
echo "  - Check Instagram every 5 minutes"
echo "  - Auto-restart on crash"
echo "  - Survive system reboot"
echo "  - Log to AI_Employee_Vault/Logs/instagram_watcher.log"
echo ""
