FROM python:3.12-slim

# Install necessary system packages for database tools and health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker caching
# Copy requirements files (including the lock)
COPY requirements-lock.txt ./ 

# Install dependencies from the lock file
RUN pip3 install --no-cache-dir -r requirements-lock.txt

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
