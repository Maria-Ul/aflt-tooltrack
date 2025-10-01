# Fetching the latest node image on apline linux
FROM node:alpine AS builder

# Declaring env
ENV NODE_ENV development

# Setting up the work directory
WORKDIR /app

# Installing dependencies
COPY ./front/package.json ./front/package-lock.json ./
RUN npm install

# Copying all the files in our project
COPY ./front/. .

# Building our application
# RUN npm run build

ENTRYPOINT ["npm", "start"]
