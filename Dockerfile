# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory for the application
WORKDIR /app

# Install Python dependencies first to leverage Docker cache
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code into the container
COPY app.py app.py

# Expose the application's port
EXPOSE 5000

# Default command to run the app using gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
