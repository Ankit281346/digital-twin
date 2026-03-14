# Use an official Python runtime as a parent image (3.11 is stable)
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port (Render sets the PORT env var automatically, default is 10000)
EXPOSE 10000

# Run the application
# Use shell form to expand $PORT variable properly
CMD sh -c "uvicorn server:app --host 0.0.0.0 --port ${PORT:-10000}"
