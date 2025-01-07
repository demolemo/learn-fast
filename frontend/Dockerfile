# Use Node as the base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files first to leverage Docker caching
COPY package*.json ./

# Install dependencies
RUN npm install react react-dom @babel/core @babel/preset-react \
    babel-loader webpack webpack-cli webpack-dev-server \
    style-loader css-loader

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Expose the port the app runs on (3000)
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
