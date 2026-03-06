#!/bin/bash

# Start the FastAPI application in the background
echo "Starting FastAPI server..."
uvicorn api.main:app --host 0.0.0.0 --port 7860 &

# Start the Telegram Bot in the foreground
echo "Starting Telegram Bot..."
python telegram_bot.py
