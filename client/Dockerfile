# Use the official Node.js image as the base image
FROM node:18 AS build

WORKDIR /app

COPY ./ /app

# Replace .env with .env.prod in the container
COPY .env.prod /app/.env

RUN npm install

RUN npm run build:web

# Stage 2: Serve the React app using nginx
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf 

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
