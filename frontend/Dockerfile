# Use an existing node alpine image as a base image.
FROM node:18-alpine

# Set the working directory.
WORKDIR /app

# Copy the package.json file.
COPY package.json .

# Install application dependencies.
RUN npm install

# Copy the rest of the application files.
COPY . .

# Build application and install runner.
RUN npm run build
RUN npm install -g serve

# Expose the port.
EXPOSE 3000

# Run the application.
CMD ["serve", "-s", "build"]