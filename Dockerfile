FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create log directory
RUN mkdir -p /app/logs

# Copy application code
COPY . .

# Expose ports
EXPOSE 8080 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_DIRECTORY=/app/logs

# Run the application
CMD ["python", "main.py"]