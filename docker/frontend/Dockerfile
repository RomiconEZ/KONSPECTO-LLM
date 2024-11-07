# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Установка зависимостей
COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps

# Копирование исходного кода
COPY frontend/ .

EXPOSE 3000

ENV HOST=0.0.0.0
ENV PORT=3000

# Использование команды dev для разработки
CMD ["npm", "run", "dev", "--", "--host"]