#!/usr/bin/env bash
set -e

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js for frontend build (Render Python env doesn't include it)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash - 2>/dev/null || true
apt-get install -y nodejs 2>/dev/null || true

# If apt isn't available, try using the pre-installed node
if ! command -v node &>/dev/null; then
  echo "Node.js not found via apt, checking PATH..."
  export PATH="/usr/local/bin:/usr/bin:$PATH"
fi

echo "Node version: $(node --version 2>/dev/null || echo 'not found')"
echo "npm version: $(npm --version 2>/dev/null || echo 'not found')"

# Build frontend
cd frontend
npm install
npm run build
cd ..

echo "Build complete"
