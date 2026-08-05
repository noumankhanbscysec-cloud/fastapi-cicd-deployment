#!/bin/bash

set -e

echo "Starting deployment..."

cd /home/robot/fb_clone-website

echo "Pulling latest code..."
git pull origin main

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Restarting FastAPI service..."
sudo systemctl restart fastapi

echo "Deployment completed!"
