# Dockerfile for Nginx SSL termination
FROM nginx:1.25-alpine

# Install envsubst for environment variable substitution
RUN apk add --no-cache gettext

# Copy nginx configuration template
COPY nginx.conf /etc/nginx/nginx.conf.template

# Create directories for SSL certificates
RUN mkdir -p /etc/nginx/ssl/live/mcp.coderweb.ru /var/www/certbot

# Expose ports
EXPOSE 80 443

# Start nginx with env substitution
CMD envsubst '$DOMAIN' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && nginx -g 'daemon off;'
