#!/bin/bash

echo "Setting up the project..."
echo "It will take few time......."

# Navigate to Next.js folder and install dependencies
echo "Installing Next.js frontend dependencies..."
cd nextjs
npm install
cd ..

# Navigate to agent and set up virtual environment
echo "Setting up agent environment..."
cd agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# Navigate to Flask API and set up virtual environment
echo "Setting up Flask backend environment..."
cd flask
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

echo "Setup complete!"
