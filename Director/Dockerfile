# Stage 1: Build Frontend
FROM node:20 AS frontend-build
WORKDIR /app/frontend

# Copy frontend dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source
COPY frontend/ ./

# Build the React app
RUN npm run build

# Stage 2: Runtime with Frontend + Director Backend
FROM python:3.13-slim

# Install Nginx and FFmpeg
RUN apt-get update && apt-get install -y \
    nginx \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared auth module
COPY auth.py .

# Copy Director service code
COPY Director/ ./Director/

# Copy built frontend from Stage 1
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# Copy Cloud Run specific Nginx configuration
COPY Director/nginx-cloudrun.conf /etc/nginx/nginx.conf

# Copy Cloud Run specific start script
COPY Director/start-cloudrun.sh /app/start.sh
RUN chmod +x /app/start.sh

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Start Nginx and Director service
CMD ["/app/start.sh"]
