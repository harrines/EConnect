# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (Railway will set PORT env variable)
EXPOSE 8000

# Command to run the application
CMD ["sh", "-c", "uvicorn Server:app --host 0.0.0.0 --port ${PORT:-8000}"]
