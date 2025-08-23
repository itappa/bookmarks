# Stage 1: Node.jsによるビルド
FROM node:22.17.1 AS node-build
WORKDIR /app
COPY package*.json ./
RUN npm install -g npm@latest
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Pythonで実行
FROM python:3.12 AS base
WORKDIR /app
RUN apt-get update
COPY --from=node-build /app/static ./static
COPY --from=node-build /app/node_modules ./node_modules
COPY --from=node-build /app/package.json ./package.json
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install uv
RUN uv pip install --system -r requirements.txt
COPY . .


FROM base AS web
