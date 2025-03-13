#!/bin/bash

# Start all servers in the background
echo -e "\e[32mStarting LiveKit server...\e[0m"
cd livekit 
source venv/bin/activate 
python agent.py dev &
LIVEKIT_PID=$!
cd ..

echo -e "\e[32mStarting backend server...\e[0m"
cd backend 
source venv/bin/activate 
gunicorn -w 4 -b 0.0.0.0:5000 app:app & 
FLASK_PID=$!
cd ..

echo -e "\e[32mStarting frontend server...\e[0m"
cd frontend 
npm run dev & 
NEXT_PID=$!
cd ..

# Function to kill all processes when Ctrl+C is pressed
cleanup() {
  echo -e "\e[31mStopping all servers...\e[0m"
  kill $FLASK_PID $NEXT_PID $LIVEKIT_PID
  wait
  echo -e "\e[34mAll servers stopped.\e[0m"
  exit 0
}

# Trap Ctrl+C and call cleanup function
trap cleanup SIGINT

# Keep script running to maintain background processes
wait
