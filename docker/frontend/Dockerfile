# docker/frontend/Dockerfile

# Stage 1: Build the React application
FROM node:18-alpine AS build

WORKDIR /app

# Define a build argument for VITE_API_URL с дефолтным значением
ARG VITE_API_URL=/api

# Set the environment variable for the build
ENV VITE_API_URL=${VITE_API_URL}

# Копирование файлов package.json и package-lock.json
COPY frontend/package*.json ./

# Установка зависимостей
RUN npm ci

# Копирование исходного кода
COPY frontend/ ./

# Сборка приложения
RUN npm run build

# Stage 2: Serve the built app with Nginx
FROM nginx:alpine

# Удаление стандартного сайта Nginx
RUN rm -rf /usr/share/nginx/html/*

# Копирование построенных файлов из предыдущей сборки
COPY --from=build /app/dist /usr/share/nginx/html

# Копирование пользовательской конфигурации Nginx
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Открытие порта 80
EXPOSE 80

# Запуск Nginx
CMD ["nginx", "-g", "daemon off;"]