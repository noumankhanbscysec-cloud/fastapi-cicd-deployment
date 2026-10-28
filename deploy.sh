
#!/bin/bash
set -e

APP_DIR="/home/ec2-user/fastapi-cicd-deployment"

echo "Starting FastAPI deployment..."

cd "$APP_DIR"

echo "Pulling latest code..."
git pull --ff-only origin main

echo "Activating virtual environment..."
source "$APP_DIR/venv/bin/activate"

echo "Installing dependencies..."
python -m pip install -r requirements.txt

echo "Restarting FastAPI service..."
sudo systemctl restart fastapi

echo "Waiting for FastAPI to become ready..."

for i in {1..15}; do
    if curl --fail --silent --max-time 2 \
        http://127.0.0.1:8000/ > /dev/null; then
        echo "API is responding!"
        break
    fi

    if [ "$i" -eq 15 ]; then
        echo "ERROR: FastAPI did not become ready."
        sudo systemctl status fastapi --no-pager || true
        sudo journalctl -u fastapi -n 40 --no-pager || true
        exit 1
    fi

    sleep 2
done

echo "Testing API response..."
curl --fail --show-error --max-time 5 http://127.0.0.1:8000/

echo
echo "Deployment completed successfully!"

