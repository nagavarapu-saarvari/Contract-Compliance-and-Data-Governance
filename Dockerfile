# ---------- Base Image (Python) ----------
FROM python:3.11 AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libxcb1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Set working directory
WORKDIR /app

# Copy project
COPY . .

# Install Python + frontend dependencies
RUN pip install --no-cache-dir pipenv \
    && cd backend && pipenv install --deploy \
    && cd ../frontend && npm install && npm run build

# Expose ports
EXPOSE 8001 3000

# ---------- Default Command ----------
CMD sh -c "sleep 10 && \
           cd /app/backend && pipenv run python setup_db.py && pipenv run start & \
           sleep 20 && \
           cd /app/frontend && npm start"