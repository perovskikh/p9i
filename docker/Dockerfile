# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Build args for API keys (optional - can be passed at build time)
ARG MINIMAX_API_KEY
ARG ZAI_API_KEY
ARG OPENROUTER_API_KEY
ARG DEEPSEEK_API_KEY
ARG ANTHROPIC_API_KEY
ARG P9I_API_KEY
ARG JWT_SECRET
ARG JWT_ENABLED=false
ARG DOMAIN=localhost

# Write API keys to .env file during build (if provided)
RUN if [ -n "$MINIMAX_API_KEY" ]; then \
        echo "MINIMAX_API_KEY=$MINIMAX_API_KEY" >> /app/.env; \
    fi && \
    if [ -n "$ZAI_API_KEY" ]; then \
        echo "ZAI_API_KEY=$ZAI_API_KEY" >> /app/.env; \
    fi && \
    if [ -n "$OPENROUTER_API_KEY" ]; then \
        echo "OPENROUTER_API_KEY=$OPENROUTER_API_KEY" >> /app/.env; \
    fi && \
    if [ -n "$DEEPSEEK_API_KEY" ]; then \
        echo "DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY" >> /app/.env; \
    fi && \
    if [ -n "$ANTHROPIC_API_KEY" ]; then \
        echo "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" >> /app/.env; \
    fi && \
    if [ -n "$P9I_API_KEY" ]; then \
        echo "P9I_API_KEY=$P9I_API_KEY" >> /app/.env; \
    fi && \
    if [ -n "$JWT_SECRET" ]; then \
        echo "JWT_SECRET=$JWT_SECRET" >> /app/.env; \
    fi && \
    if [ -n "$JWT_ENABLED" ]; then \
        echo "JWT_ENABLED=$JWT_ENABLED" >> /app/.env; \
    fi && \
    if [ -n "$DOMAIN" ]; then \
        echo "DOMAIN=$DOMAIN" >> /app/.env; \
    fi

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set Playwright cache path before installation
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY config/ ./config/
COPY tests/ ./tests/

# Install dependencies (including dev for pytest)
RUN uv pip install --system -r pyproject.toml
RUN uv pip install --system ".[dev]"

# Install Playwright browsers
RUN playwright install chromium && \
    playwright install-deps chromium

# Create non-root user
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Expose MCP port and Web UI port
EXPOSE 8000 8080

# Health check for SSE mode only (when transport=sse, server listens on port 8000)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=5 \
    CMD python3 -c "import socket; s=socket.socket(); s.connect(('localhost', 8000)); s.close()" 2>/dev/null || exit 1

# Run MCP server
# Default: stdio for Claude Code compatibility
# Set MCP_TRANSPORT=sse for HTTP mode
ENV MCP_TRANSPORT=stdio

# API Keys (from build args or defaults)
ENV MINIMAX_API_KEY=${MINIMAX_API_KEY}
ENV ZAI_API_KEY=${ZAI_API_KEY}
ENV OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
ENV DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
ENV ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
ENV P9I_API_KEY=${P9I_API_KEY:-sk-p9i-dev}
ENV JWT_SECRET=${JWT_SECRET:-dev-secret-change-in-production}
ENV JWT_ENABLED=${JWT_ENABLED}
ENV DOMAIN=${DOMAIN}

CMD ["python", "-m", "src.api.server"]
