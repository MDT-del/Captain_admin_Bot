# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the cache, which reduces the image size.
# --trusted-host pypi.python.org: Can help in some environments with SSL/TLS issues.
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . .

# Create an empty database file so that the volume mount doesn't create a directory
RUN touch /app/bot.db

# Define the command to run your app
# This will execute 'python bot.py' when the container starts
CMD ["python", "bot.py"]
