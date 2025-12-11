# Stage 1: Build Frontend
FROM node:20 AS frontend-build
WORKDIR /app/frontend
# Copy dependency definitions
COPY frontend/package*.json ./
RUN npm install
# Copy source code
COPY frontend/ ./
# Build the React app
RUN npm run build

# Stage 2: Runtime Environment
FROM python:3.10-slim

# Install system dependencies (Nginx, FFmpeg)
RUN apt-get update && apt-get install -y \
    nginx \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy python requirements
COPY requirements.txt .
# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code
COPY . .

# Copy built frontend from Stage 1
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# Copy configuration files
COPY nginx.conf /etc/nginx/nginx.conf
COPY start.sh /app/start.sh

# Make start script executable
RUN chmod +x /app/start.sh

# Expose the Cloud Run port
ENV PORT=8080
EXPOSE 8080

# Start command
CMD ["/app/start.sh"]
