# Fetching the latest node image on apline linux
FROM node:alpine AS builder

# Declaring env
ENV NODE_ENV development

# Setting up the work directory
WORKDIR /app

# Copying all the files in our project
COPY ./front/. .

RUN npm install

# Building our application
# RUN npm run build

ENTRYPOINT ["npm", "start"]
