# Use a lightweight Python image from the official Docker repository
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory (where the Dockerfile resides) into the container's working directory
COPY . /app

# Install the system dependencies needed for the Flask app
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port Flask will run on (default is 8000)
EXPOSE 8000

# Set the environment variable to automatically load the environment variables from .env
ENV FLASK_ENV=development

# Command to run the Flask app when the container starts
CMD ["python", "app.py"]
