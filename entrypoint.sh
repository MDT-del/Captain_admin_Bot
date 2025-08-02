#!/bin/sh

# Create the data directory if it doesn't exist
mkdir -p /app/data

# Ensure the database file exists before starting the app
touch /app/data/bot.db

# Execute the main command (passed from Dockerfile's CMD)
exec "$@"
