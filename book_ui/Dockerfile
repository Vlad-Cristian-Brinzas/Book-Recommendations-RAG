# Slim node image for build
FROM node:24-alpine AS build

# Set working directory
WORKDIR /book_ui

# Copy package files and install dependencies
# COPY book_ui/package.json book_ui/package-lock.json ./
# RUN npm ci
# ^ Use in prod, once we have package-lock.json
COPY book_ui/package.json ./
RUN npm install

# Copy rest of the project files and build the app
COPY book_ui/ .

# Build the React app
RUN npm run build


# Use a lightweight web server to serve the built app
FROM nginx:alpine

# Copy configuration file for Nginx
COPY book_ui/nginx/nginx.conf /etc/nginx/nginx.conf

# Copy built files from the build stage
COPY --from=build /book_ui/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]