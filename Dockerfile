# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
# Try PyPI first, fallback to GitHub if needed
RUN pip install --no-cache-dir requests>=2.31.0 && \
    (pip install --no-cache-dir mcp>=0.9.0 || \
     pip install --no-cache-dir git+https://github.com/modelcontextprotocol/python-sdk.git)

# Copy the MCP server code
COPY mcp_server.py .

# Make the script executable
RUN chmod +x mcp_server.py

# Set the entrypoint
ENTRYPOINT ["python", "mcp_server.py"]

# The MCP server communicates via stdio, so we don't expose any ports
# Environment variable DIGITALOCEAN_API_TOKEN should be passed at runtime

