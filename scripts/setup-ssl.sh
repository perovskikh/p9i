#!/bin/bash
# setup-ssl.sh - SSL certificate setup for mcp.coderweb.ru

set -e

DOMAIN="mcp.coderweb.ru"
EMAIL="admin@coderweb.ru"  # Change to your email
SSL_DIR="./nginx/ssl"
CERTBOT_DIR="./nginx/certbot-www"

echo "Setting up SSL certificates for $DOMAIN..."

# Create directories
mkdir -p "$SSL_DIR" "$CERTBOT_DIR"

# Option 1: Use Let's Encrypt (recommended for production)
setup_letsencrypt() {
    echo "Setting up Let's Encrypt certificates..."

    # Check if certbot is available
    if command -v certbot &> /dev/null; then
        certbot certonly --standalone \
            -d "$DOMAIN" \
            --email "$EMAIL" \
            --agree-tos \
            --non-interactive \
            --force-renewal

        # Copy certificates
        cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/fullchain.pem"
        cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/privkey.pem"

        echo "Let's Encrypt certificates installed successfully!"
    else
        echo "Certbot not found. Please install certbot:"
        echo "  Ubuntu/Debian: sudo apt-get install certbot"
        echo "  CentOS/RHEL: sudo yum install certbot"
        return 1
    fi
}

# Option 2: Generate self-signed certificates (for development)
setup_self_signed() {
    echo "Generating self-signed SSL certificates..."

    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/privkey.pem" \
        -out "$SSL_DIR/fullchain.pem" \
        -subj "/C=RU/ST=State/L=City/O=Organization/CN=$DOMAIN" \
        -addext "subjectAltName=DNS:$DOMAIN,DNS:www.$DOMAIN"

    echo "Self-signed certificates generated!"
    echo "WARNING: Self-signed certificates will cause browser warnings!"
}

# Check which SSL setup to use
if [ "$1" == "letsencrypt" ]; then
    setup_letsencrypt
elif [ "$1" == "self-signed" ]; then
    setup_self_signed
else
    echo "Usage: $0 [letsencrypt|self-signed]"
    echo ""
    echo "For production with Let's Encrypt:"
    echo "  $0 letsencrypt"
    echo ""
    echo "For development with self-signed certificates:"
    echo "  $0 self-signed"
    exit 1
fi

# Set proper permissions
chmod 600 "$SSL_DIR/privkey.pem"
chmod 644 "$SSL_DIR/fullchain.pem"

echo ""
echo "SSL certificates installed in $SSL_DIR"
echo "Starting services with docker-compose.ssl.yml..."
