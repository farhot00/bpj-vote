FROM ubuntu:latest
LABEL authors="mohammad"

ENTRYPOINT ["top", "-b"]FROM python:3.12-slim

# Install necessary system packages for database tools and health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt requirements-lock.txt* ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Ensure entrypoint script is executable
RUN chmod +x entrypoint.sh

# Expose application port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Default command (Gunicorn for Django WSGI)
CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:8000", "bpjvote.wsgi:application"]
