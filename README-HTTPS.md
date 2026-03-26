# HTTPS Setup for p9i MCP Server

This guide covers setting up HTTPS access for the p9i MCP server on `mcp.coderweb.ru`.

## Prerequisites

- Domain pointing to your server: `mcp.coderweb.ru` → `144.31.76.95`
- Docker and Docker Compose installed
- Root or sudo access (for port 80/443)

## Architecture

```
Client (HTTPS) → Nginx (SSL Termination) → MCP Server (HTTP)
```

## Quick Start

### 1. Self-Signed Certificates (Development)

```bash
# Generate self-signed certificates
./scripts/setup-ssl.sh self-signed

# Start with SSL
docker compose -f docker-compose.ssl.yml up -d
```

**Access:** `https://mcp.coderweb.ru` (browser will show security warning)

### 2. Let's Encrypt Certificates (Production)

```bash
# Install certbot (Ubuntu/Debian)
sudo apt-get install certbot

# Get certificates
./scripts/setup-ssl.sh letsencrypt

# Start with SSL
docker compose -f docker-compose.ssl.yml up -d
```

**Access:** `https://mcp.coderweb.ru` (valid SSL certificate)

## Configuration Files

- `nginx/nginx.conf` - Nginx SSL termination configuration
- `nginx/Dockerfile` - Nginx container build
- `docker-compose.ssl.yml` - SSL-enabled Docker Compose
- `scripts/setup-ssl.sh` - SSL certificate setup script

## Environment Variables

Key environment variables in `.env`:

```env
# Domain configuration
DOMAIN=coderweb.ru

# SSL settings
SSL_ENABLED=true
SSL_CERT_PATH=/etc/nginx/ssl/live/mcp.coderweb.ru/fullchain.pem
SSL_KEY_PATH=/etc/nginx/ssl/live/mcp.coderweb.ru/privkey.pem

# MCP Server settings
MCP_TRANSPORT=sse
SERVER_HOST=0.0.0.0
ALLOWED_ORIGINS=https://mcp.coderweb.ru,https://coderweb.ru
```

## Testing HTTPS

### Test SSL Certificate

```bash
# Check SSL certificate
openssl s_client -connect mcp.coderweb.ru:443 -servername mcp.coderweb.ru

# Test with curl
curl -k https://mcp.coderweb.ru/health
```

### Test MCP Connection

```bash
# Test MCP endpoint
curl -X POST https://mcp.coderweb.ru/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

## DNS Configuration

Ensure your DNS is configured:

```
A Record: mcp.coderweb.ru → 144.31.76.95
```

## Firewall Configuration

Open necessary ports:

```bash
# Allow HTTP (for Let's Encrypt)
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Allow internal Docker communication
sudo ufw allow from 172.16.0.0/12
```

## SSL Certificate Renewal

### Automatic Renewal

The `certbot` service in `docker-compose.ssl.yml` handles automatic renewal every 12 hours.

### Manual Renewal

```bash
# Renew certificates
sudo certbot renew

# Restart nginx to apply new certificates
docker compose -f docker-compose.ssl.yml restart nginx
```

## Troubleshooting

### Certificate Issues

```bash
# Check certificate validity
openssl x509 -in nginx/ssl/fullchain.pem -text -noout

# Check nginx logs
docker compose -f docker-compose.ssl.yml logs nginx

# Restart nginx
docker compose -f docker-compose.ssl.yml restart nginx
```

### Connection Issues

```bash
# Check if ports are open
netstat -tlnp | grep -E ':(80|443|8000)'

# Check DNS resolution
nslookup mcp.coderweb.ru

# Test connectivity
telnet mcp.coderweb.ru 443
```

## MCP Client Configuration

### For Claude Code

Update `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "p9i-https": {
      "url": "https://mcp.coderweb.ru/mcp",
      "transport": "sse"
    }
  }
}
```

### For Other MCP Clients

```javascript
// SSE Transport
const mcpClient = new MCPClient({
  url: 'https://mcp.coderweb.ru/mcp',
  transport: 'sse',
  headers: {
    'Authorization': 'Bearer YOUR_P9I_API_KEY'
  }
});
```

## Security Considerations

1. **Use Let's Encrypt** for production (valid certificates)
2. **Enable HTTP/2** for better performance
3. **Set up firewall rules** to restrict access
4. **Monitor SSL expiry** and renew before expiration
5. **Use strong API keys** and rotate them regularly
6. **Enable rate limiting** to prevent abuse

## Performance Tuning

### Nginx Optimization

Edit `nginx/nginx.conf`:

```nginx
# Increase worker connections
worker_processes auto;
worker_connections 2048;

# Enable gzip compression
gzip on;
gzip_types text/plain application/json;

# Increase buffer sizes
client_body_buffer_size 128k;
client_max_body_size 10m;
```

### MCP Server Optimization

Edit `docker-compose.ssl.yml`:

```yaml
mcp-server:
  environment:
    - WORKERS=4
    - MAX_CONNECTIONS=100
```

## Monitoring

### Health Checks

```bash
# Check MCP server health
curl https://mcp.coderweb.ru/health

# Check nginx status
curl https://mcp.coderweb.ru/nginx-health
```

### Logs

```bash
# All services
docker compose -f docker-compose.ssl.yml logs -f

# Specific service
docker compose -f docker-compose.ssl.yml logs -f nginx
docker compose -f docker-compose.ssl.yml logs -f mcp-server
```

## Backup and Recovery

### Backup SSL Certificates

```bash
# Backup SSL certificates
tar -czf ssl-backup-$(date +%Y%m%d).tar.gz nginx/ssl/
```

### Restore from Backup

```bash
# Restore SSL certificates
tar -xzf ssl-backup-YYYYMMDD.tar.gz
```

## Next Steps

1. Configure DNS records
2. Obtain SSL certificates
3. Test HTTPS connectivity
4. Configure firewall rules
5. Set up monitoring
6. Update MCP client configurations
