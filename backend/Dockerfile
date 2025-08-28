# Use Python 3.11 slim image for faster builds
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for faster builds
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "src/main.py"]
