FROM node:22-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci --omit=dev

COPY . .

ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

EXPOSE 3000

CMD ["node", "server.js"]