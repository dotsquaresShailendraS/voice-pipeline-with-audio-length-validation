#!/bin/bash

echo "Setting up the project..."
echo "It will take few time......."

# Navigate to Next.js folder and install dependencies
echo "Installing Next.js frontend dependencies..."
cd frontend
npm install
cd ..

# Navigate to LiveKit and set up virtual environment
echo "Setting up LiveKit environment..."
cd livekit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python agent.py download-files
deactivate
cd ..

# Navigate to Flask API and set up virtual environment
echo "Setting up Flask backend environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

echo "Setup complete!"
