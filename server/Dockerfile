FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Cloud Run uses port 8080 by default
EXPOSE 8080

# Run with uvicorn — PORT env var is set by Cloud Run
CMD ["python", "main.py"]
