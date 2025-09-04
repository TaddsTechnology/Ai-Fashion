# Use Node.js 18 as the base image
FROM node:18-alpine

# Install wget for health checks
RUN apk add --no-cache wget

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Clear npm cache and install dependencies
RUN npm cache clean --force

# Install dependencies (including devDependencies for build)
# Remove package-lock.json and reinstall to fix rollup issue
RUN rm -f package-lock.json && npm install

# Copy the rest of the application code
COPY . .

# Accept build arguments for environment variables
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}

# Build the application
RUN npm run build

# Expose port 3000
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Install serve globally for production
RUN npm install -g serve

# Command to run the application
# Use PORT environment variable for Render compatibility
CMD ["sh", "-c", "serve -s dist -l ${PORT:-3000} -n"]
