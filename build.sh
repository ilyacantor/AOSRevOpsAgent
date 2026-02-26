#!/usr/bin/env bash
set -e

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Checking for Node.js ==="
if command -v node &>/dev/null; then
  echo "Node: $(node --version)"
  echo "npm: $(npm --version)"
else
  echo "Node.js not found, installing via nvm..."
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
  nvm install 20
  nvm use 20
  echo "Node: $(node --version)"
  echo "npm: $(npm --version)"
fi

echo "=== Building frontend ==="
cd frontend
npm install
npm run build
cd ..

echo "=== Build complete ==="
