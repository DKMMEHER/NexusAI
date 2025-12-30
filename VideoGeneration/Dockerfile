FROM python:3.13-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared auth module
COPY auth.py .

# Copy service-specific code
COPY VideoGeneration/ ./VideoGeneration/

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run the service
CMD ["uvicorn", "VideoGeneration.backend:app", "--host", "0.0.0.0", "--port", "8080"]
