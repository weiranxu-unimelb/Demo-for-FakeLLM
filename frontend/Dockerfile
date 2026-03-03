FROM node:20-alpine AS build

WORKDIR /app

COPY package.json /app/package.json
RUN npm install

COPY . /app

# 让前端走同域 /api，便于部署（由 nginx 反代到 backend）
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

