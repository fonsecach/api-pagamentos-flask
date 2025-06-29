FROM python:3.13-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager globally
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Make uv available system-wide
RUN cp /root/.local/bin/uv /usr/local/bin/uv

# Create non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Set working directory and change ownership
WORKDIR /app
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Copy dependency files first for better layer caching
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# Create virtual environment and install dependencies
RUN uv venv .venv
RUN uv sync

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy application source code
COPY --chown=appuser:appuser . .

# Expose port
EXPOSE 8080

# Use uv run to ensure proper virtual environment activation
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]