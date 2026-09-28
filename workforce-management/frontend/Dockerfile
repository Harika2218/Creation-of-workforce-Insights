# ===================================================================
# AI-Powered Workforce Management Automation System
# Production Frontend Container Image (Multi-Stage Build)
# ===================================================================

# Stage 1: Build the React Application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency definitions
COPY package.json package-lock.json ./

# Install exact npm dependencies
RUN npm ci

# Copy source code and config
COPY . .

# Build production bundle with TypeScript check
RUN npm run build

# Stage 2: Serve optimized assets with Nginx
FROM nginx:1.27-alpine-slim

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose HTTP port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/ || exit 1

# Start Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
