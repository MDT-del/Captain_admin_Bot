#!/bin/sh

# Ensure the database file exists before starting the app
# This prevents docker from creating a directory if the volume is mounted from a non-existent file
touch /app/bot.db

# Execute the main command (passed from Dockerfile's CMD)
# Using "exec" means the Python process will replace the shell process,
# which is better for signal handling (e.g., stopping the container).
exec "$@"
