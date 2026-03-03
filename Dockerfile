# ---------- Stage 1: Build React ----------
FROM node:18 && python:3.11

WORKDIR /app
COPY . .
RUN cd frontend && npm install && npm run build && apt-get update && apt-get install -y \
        gcc \
        libpq-dev \
        libgl1 \
        libglib2.0-0 \
        libxext6 \
        libsm6 \
        libxrender1 \
        libxcb1 \
    && rm -rf /var/lib/apt/lists/*

RUN cd backend && pip install pipenv && pipenv install --deploy

EXPOSE 8001 3002

CMD ["pipenv", "run", "start"]