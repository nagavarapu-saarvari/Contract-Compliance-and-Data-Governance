# ---------- Base Image (Python) ----------
FROM python:3.11-slim AS base

# Install system dependencies (node + pipenv + others) and Node.js in one layer
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Set working directory
WORKDIR /app

# Copy dependency files and install all dependencies in one layer
COPY . .
RUN pip install --no-cache-dir pipenv && cd backend && pipenv install --deploy && cd .. && cd frontend && npm install && npm run build 

# Expose backend + frontend ports
EXPOSE 8001 3000

# ---------- Default Command ----------
# Start both backend and frontend
CMD sh -c "cd /app/backend && pipenv run start & \
           sleep 20 && \
           cd /app/frontend && npm start"