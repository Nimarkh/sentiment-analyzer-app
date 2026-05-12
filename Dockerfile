FROM node:20-alpine AS frontend-build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY angular.json tsconfig*.json proxy.conf.json ./
COPY src ./src
RUN npm run build

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY --from=frontend-build /app/backend/static ./backend/static

WORKDIR /app/backend
EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
